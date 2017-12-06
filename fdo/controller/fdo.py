import base64
import logging

from openerp import http
from openerp.osv import fields
from openerp.tools.translate import _


class FDOController(http.Controller):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self._user_id = None

        super(FDOController, self).__init__()

    @http.route(
        route="/fdo/1/action/bootstrap",
        auth="public",
        type="json",
        csrf=False
    )
    def bootstrap(self, token):
        env = http.request.env

        session_id = self._get_session(env, token)
        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        user_id = session_id.user_id
        session_obj = self._get_orm(env, user_id, "fdo.session")
        if session_id.status != session_obj.STATUS_PREPARED[0]:
            return {
                "success": False,
                "error": _("Session already worked")
            }

        job_obj = self._get_orm(env, user_id, "fdo.job")
        job_ids = job_obj.search([
            "&",
            ("status", "=", job_obj.STATUS_PREPARED[0]),
            ("session_id", "=", session_id.id)
        ])

        session_id.write({
            "status": session_obj.STATUS_WORKING[0],
            "last_contact": fields.datetime.now()
        })

        return {
            "success": True,
            "userName": user_id.name,
            "jobsIds": job_ids.ids
        }

    @http.route(
        route="/fdo/1/action/ping",
        auth="public",
        type="json",
        csrf=False
    )
    def ping(self, token):
        env = http.request.env

        session_id = self._get_session(env, token)
        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        user_id = session_id.user_id
        session_obj = self._get_orm(env, user_id, "fdo.session")
        if session_id.status != session_obj.STATUS_WORKING[0]:
            return {
                "success": False,
                "error": _("Wrong session")
            }

        session_id.write({
            "last_contact": fields.datetime.now()
        })

        return {
            "success": True,
        }

    @http.route(
        route="/fdo/1/action/getJob",
        auth="public",
        type="json",
        csrf=False
    )
    def get_job(self, token, jobId):
        env = http.request.env

        session_id = self._get_session(env, token)
        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        user_id = session_id.user_id
        session_obj = self._get_orm(env, user_id, "fdo.session")
        if session_id.status != session_obj.STATUS_WORKING[0]:
            return {
                "success": False,
                "error": _("Session already worked")
            }

        job_obj = self._get_orm(env, user_id, "fdo.job")
        job_id = job_obj.search([
            "&", "&",
            ("id", "=", jobId),
            ("status", "=", job_obj.STATUS_PREPARED[0]),
            ("session_id", "=", session_id.id)
        ], limit=1)
        if len(job_id) == 0:
            return {
                "success": False,
                "error": _("Job not found")
            }

        job_id.write({
            "status": job_obj.STATUS_WORKING[0]
        })

        return {
            "success": True,
            "action": job_id.action,
            "attachmentId": job_id.attachment_id.id
        }

    @http.route(
        route="/fdo/1/action/getAttachment",
        auth="public",
        type="json",
        csrf=False
    )
    def get_attachment(self, token, jobId, attachmentId):
        env = http.request.env

        session_id = self._get_session(env, token)
        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        user_id = session_id.user_id
        session_obj = self._get_orm(env, user_id, "fdo.session")
        if session_id.status != session_obj.STATUS_WORKING[0]:
            return {
                "success": False,
                "error": _("Session already worked")
            }

        job_obj = self._get_orm(env, user_id, "fdo.job")
        job_id = job_obj.search([
            "&", "&",
            ("id", "=", jobId),
            ("status", "=", job_obj.STATUS_WORKING[0]),
            ("session_id", "=", session_id.id)
        ], limit=1)
        if len(job_id) == 0:
            return {
                "success": False,
                "error": _("Job not found")
            }

        attachment_id = job_id.attachment_id
        if attachment_id.id != attachmentId:
            return {
                "success": False,
                "error": _("Attachment not found")
            }

        return {
            "success": True,
            "content": attachment_id.datas
        }

    @http.route(
        route="/fdo/1/action/uploadSigned",
        auth="public",
        type="json",
        csrf=False
    )
    def upload_signed(self, token, jobId, attachmentId, signedContent):
        env = http.request.env

        session_id = self._get_session(env, token)
        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        user_id = session_id.user_id
        session_obj = self._get_orm(env, user_id, "fdo.session")
        if session_id.status != session_obj.STATUS_WORKING[0]:
            return {
                "success": False,
                "error": _("Session already worked")
            }

        job_obj = self._get_orm(env, user_id, "fdo.job")
        job_id = job_obj.search([
            "&", "&",
            ("id", "=", jobId),
            ("status", "=", job_obj.STATUS_WORKING[0]),
            ("session_id", "=", session_id.id)
        ], limit=1)
        if len(job_id) == 0:
            return {
                "success": False,
                "error": _("Job not found")
            }

        attachment_id = job_id.attachment_id
        if attachment_id.id != attachmentId:
            return {
                "success": False,
                "error": _("Attachment not found")
            }

        binary_content = base64.b64decode(signedContent)
        if len(binary_content) == 0:
            return {
                "success": False,
                "error": _("Empty data")
            }

        attachment_name = "signed-%s" % attachment_id.name
        attachment_datas_fname = "signed-%s" % str(attachment_id.datas_fname)

        ir_attachment_obj = self._get_orm(env, user_id, "ir.attachment")
        signed_attachment_id = ir_attachment_obj.create({
            "name": attachment_name,
            "datas_fname": attachment_datas_fname,
            "type": "binary",
            "datas": signedContent,
            "res_model": attachment_id.res_model,
            "res_id": attachment_id.res_id,
            "original_attachment_id": attachment_id.id
        })

        attachment_id.write({
            "signed_attachment_id": [(4, signed_attachment_id.id)]
        })

        job_id.write({
            "status": job_obj.STATUS_COMPLETED[0]
        })

        self._sanitize_session(env, session_id.id)

        return {
            "success": True,
        }

    @staticmethod
    def _get_session(env, token):
        session_id = env["fdo.session"].sudo().search([
            ("token", "=", token)
        ], limit=1)

        return session_id

    @staticmethod
    def _get_orm(env, user, model):
        return env[model].sudo(user=user)

    @staticmethod
    def _sanitize_session(env, sessionid):
        session_obj = env["fdo.session"].sudo()
        job_obj = env["fdo.job"].sudo()

        session_id = session_obj.search([
            ("id", "=", sessionid)
        ], limit=1)
        if len(session_id) == 0:
            return

        job_total = job_obj.search([
            ("session_id", "=", session_id.id)
        ], count=True)
        if job_total == 0:
            return

        job_finish = job_obj.search([
            "&",
            ("session_id", "=", session_id.id),
            ("status", "in", [job_obj.STATUS_COMPLETED[0], job_obj.STATUS_ERROR[0]])
        ], count=True)

        if job_finish == job_total:
            session_id.write({
                "status": session_obj.STATUS_COMPLETED[0]
            })
