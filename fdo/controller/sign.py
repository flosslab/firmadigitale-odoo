import json
import logging
import os

from openerp import http


class SignController(http.Controller):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._user_id = None
        super(SignController, self).__init__()

    @http.route(
        route="/fdo/sign/single/<int:sessionid>",
        auth="public",
        type="http",
        csrf=False
    )
    def sign(self, sessionid):
        env = http.request.env

        session_obj = env["fdo.session"]
        session_id = session_obj.search([("id", "=", sessionid)])
        if not session_id:
            return "Session not found"

        sing_dir = os.path.dirname(os.path.abspath(__file__))
        sign_file = os.path.join(sing_dir, "sign.html")

        fd = open(sign_file, "r")
        html_content = fd.read()
        fd.close()

        html_content = html_content.replace("####SESSION_ID####", str(sessionid))
        html_content = html_content.replace("####SESSION_LINK####", session_id.link)

        html_content = html_content.replace("####STATUS_COMPLETED####", session_obj.STATUS_COMPLETED[0])
        html_content = html_content.replace("####STATUS_ERROR####", session_obj.STATUS_ERROR[0])

        return html_content

    @http.route(
        route="/fdo/session/status",
        auth="public",
        type="json",
        csrf=False
    )
    def status(self, sessionId):
        env = http.request.env

        session_obj = env["fdo.session"]
        session_id = session_obj.search([("id", "=", sessionId)])
        if not session_id:
            return {
                "success": False,
                "error": "Session not found"
            }

        if session_id.status in [session_obj.STATUS_COMPLETED[0], session_obj.STATUS_ERROR[0]]:
            job_obj = env["fdo.job"]
            job_id = job_obj.search([
                ("session_id", "=", session_id.id)
            ], limit=1)

            if len(job_id) > 0:
                attachment_id = job_id.attachment_id
                redirect_url = self._generate_redirect_url(
                    obj_model="ir.attachment",
                    obj_id=attachment_id.signed_attachment_id[0].id,
                    view_type="form",
                    menu_id=env.ref("fdo.menu_fdo_tool_mysigned").id,
                    action=env.ref("fdo.action_irattachment_list_signed").id
                )

                return json.dumps({
                    "success": True,
                    "status": session_id.status,
                    "redirect_url": redirect_url
                })

        return json.dumps({
            "success": True,
            "status": session_id.status,
        })

    @staticmethod
    def _get_session(env, sessionid):
        return env["fdo.session"].sudo().browse(sessionid)

    @staticmethod
    def _get_orm(env, user, model):
        return env[model].sudo(user=user)

    @staticmethod
    def _generate_redirect_url(obj_model, obj_id, view_type, menu_id, action):
        items = []

        if obj_model:
            items.append("model=%s" % str(obj_model))
        if obj_id:
            items.append("id=%d" % int(obj_id))
        if view_type:
            items.append("view_type=%s" % str(view_type))
        if menu_id:
            items.append("menu_id=%d" % int(menu_id))
        if action:
            items.append("action=%d" % int(action))

        return "/web?#" + "&".join(items)
