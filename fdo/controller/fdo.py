import base64
import logging

from openerp import http
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
        job_ids = self._get_orm(env, user_id, "fdo.job").search([
            "&",
            ("processed", "=", False),
            ("session_id", "=", session_id.id)
        ])

        return {
            "success": True,
            "userName": user_id.name,
            "jobsIds": job_ids.ids
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
        job_id = self._get_orm(env, user_id, "fdo.job").search([
            "&", "&",
            ("id", "=", jobId),
            ("processed", "=", False),
            ("session_id", "=", session_id.id)
        ], limit=1)

        if len(job_id) == 0:
            return {
                "success": False,
                "error": _("Job not found")
            }

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
        job_id = self._get_orm(env, user_id, "fdo.job").search([
            "&", "&",
            ("id", "=", jobId),
            ("processed", "=", False),
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
        job_id = self._get_orm(env, user_id, "fdo.job").search([
            "&", "&",
            ("id", "=", jobId),
            ("processed", "=", False),
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
        attachment_datas_fname = "signed-" % attachment_id.datas_fname
        signed_attachment_id = self._get_orm("ir.attachment").create({
            "name": attachment_name,
            "datas_fname": attachment_datas_fname,
            "type": "binary",
            "datas": signedContent,
            "res_model": attachment_id.res_model.id,
            "res_id": attachment_id.res_id
        })

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
