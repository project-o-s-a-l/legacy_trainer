import smtplib
from email.message import EmailMessage

from backend.app.core.config import settings
from backend.app.db.enums import VerificationFlow


class EmailService:
    def send_verification_code(
        self,
        *,
        email: str,
        code: str,
        flow: VerificationFlow,
    ) -> None:
        if not settings.smtp_host or not settings.smtp_from_email:
            raise RuntimeError("SMTP is not configured")

        subject = self._build_subject(flow)
        body = self._build_body(code, flow)

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from_email
        message["To"] = email
        message.set_content(body)

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
        ) as server:
            if settings.smtp_use_tls:
                server.starttls()

            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)

            server.send_message(message)

    def _build_subject(self, flow: VerificationFlow) -> str:
        if flow == VerificationFlow.REGISTRATION:
            return "Legacy Trainer registration code"
        return "Legacy Trainer password recovery code"

    def _build_body(self, code: str, flow: VerificationFlow) -> str:
        if flow == VerificationFlow.REGISTRATION:
            return (
                "Use this code to confirm your registration:\n\n"
                f"{code}\n\n"
                "The code is valid for 10 minutes."
            )

        return (
            "Use this code to continue password recovery:\n\n"
            f"{code}\n\n"
            "The code is valid for 10 minutes."
        )
