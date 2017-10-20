import logging

from openerp import http


class FDOController(http.Controller):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        super(FDOController, self).__init__()

    @http.route(
        route="/fdo/1/action/bootstrap",
        auth="public",
        type="json",
        csrf=False
    )
    def bootstrap(self, token=""):
        env = http.request.env

        session_id = env["fdo.session"].sudo().search([
            ("token", "=", token)
        ], limit=1)

        if len(session_id) == 0:
            return {
                "success": False,
                "error": _("Token not found")
            }

        job_ids = env["fdo.job"].sudo().search([
            ("session_id", "=", token)
        ])

        return {
            "success": True,
            "user": session_id.user_id.name,
            "jobs": len(job_ids)
        }
