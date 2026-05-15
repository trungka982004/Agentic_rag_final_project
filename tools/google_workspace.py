"""
tools/google_workspace.py

Google Workspace API Tool for the Agentic RAG System.
Cho phép Agent xuất kết quả phân tích ra Google Docs hoặc Google Sheets.

SETUP (bước một lần):
    1. Truy cập https://console.cloud.google.com/ → tạo project mới.
    2. Enable "Google Docs API" và "Google Sheets API".
    3. Tạo OAuth 2.0 Client ID (loại "Desktop App"), tải file JSON về.
    4. Đổi tên file đó thành `credentials.json` và đặt vào thư mục gốc dự án.
    5. Lần chạy đầu tiên sẽ mở trình duyệt để xác thực, sau đó tạo `token.json`.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Phạm vi quyền truy cập cần thiết
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


# Fixed port - must match exactly the Authorized redirect URI in Google Cloud Console
# Add "http://localhost:8080/" to Authorized redirect URIs in Cloud Console
OAUTH_CALLBACK_PORT = 8080


def _detect_credential_type() -> str:
    """Detect whether credentials.json is 'web' or 'installed' type."""
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
        if "web" in data:
            return "web"
        elif "installed" in data:
            return "installed"
    except Exception:
        pass
    return "unknown"


def _get_google_credentials() -> Credentials | None:
    """
    Get and refresh Google OAuth2 credentials.

    Supports both credential types:
    - 'installed' (Desktop App): works out-of-the-box with InstalledAppFlow.
    - 'web' (Web Application): requires adding 'http://localhost:8080/'
      to Authorized redirect URIs in Google Cloud Console.
    """
    creds = None

    # 1. Load cached token if it exists
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    # 2. Refresh expired token
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            print(f"[Google Auth] Token refreshed and saved to '{TOKEN_FILE}'.")
            return creds
        except Exception as e:
            print(f"[Google Auth] Token refresh failed: {e}. Re-authenticating...")
            creds = None

    # 3. Trigger OAuth2 browser flow if no valid token
    if not creds:
        if not os.path.exists(CREDENTIALS_FILE):
            print(
                "[Google Auth] ERROR: 'credentials.json' not found.\n"
                "  Please download OAuth2 credentials from Google Cloud Console\n"
                "  and place them as 'credentials.json' in the project root."
            )
            return None

        cred_type = _detect_credential_type()
        print(f"[Google Auth] Credential type detected: '{cred_type}'")

        if cred_type == "web":
            print(
                "[Google Auth] NOTE: 'Web Application' credentials detected.\n"
                f"  Ensure 'http://localhost:{OAUTH_CALLBACK_PORT}/' is added to\n"
                "  Authorized redirect URIs in Google Cloud Console.\n"
                "  Path: APIs & Services > Credentials > Edit OAuth 2.0 Client"
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )
            # Use fixed port so it matches the registered redirect URI
            creds = flow.run_local_server(
                port=OAUTH_CALLBACK_PORT,
                prompt="consent",
                open_browser=True,
            )
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            print(f"[Google Auth] Authentication successful. Token saved to '{TOKEN_FILE}'.")
        except Exception as e:
            print(f"[Google Auth] Authentication failed: {e}")
            return None

    return creds


def export_to_google_docs(title: str, content: str) -> str:
    """
    Tạo một Google Docs mới và ghi nội dung vào đó.

    Args:
        title: Tiêu đề của tài liệu Google Docs.
        content: Nội dung văn bản cần ghi (plain text hoặc markdown).

    Returns:
        URL của tài liệu vừa được tạo, hoặc thông báo lỗi.
    """
    creds = _get_google_credentials()
    if not creds:
        return (
            "[Google Workspace] Chưa cấu hình. Vui lòng đặt file `credentials.json` "
            "vào thư mục gốc dự án và chạy lại để xác thực OAuth2."
        )

    try:
        docs_service = build("docs", "v1", credentials=creds)

        # 1. Tạo document rỗng với tiêu đề
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        # 2. Chèn nội dung vào vị trí đầu tài liệu
        requests_body = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": content,
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests_body}
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        print(f"[Google Docs] Đã tạo thành công: {doc_url}")
        return f"✅ Đã xuất ra Google Docs: {doc_url}"

    except Exception as e:
        return f"[Google Docs] Lỗi khi xuất: {e}"


def export_to_google_sheets(title: str, data: list[list]) -> str:
    """
    Tạo một Google Sheets mới và ghi dữ liệu dạng bảng vào đó.

    Args:
        title: Tiêu đề của spreadsheet.
        data: Dữ liệu dạng list of lists, mỗi list con là một hàng.
              Ví dụ: [["Tiêu đề 1", "Tiêu đề 2"], ["Giá trị A", "Giá trị B"]]

    Returns:
        URL của spreadsheet vừa được tạo, hoặc thông báo lỗi.
    """
    creds = _get_google_credentials()
    if not creds:
        return (
            "[Google Workspace] Chưa cấu hình. Vui lòng đặt file `credentials.json` "
            "vào thư mục gốc dự án và chạy lại để xác thực OAuth2."
        )

    try:
        sheets_service = build("sheets", "v4", credentials=creds)

        # 1. Tạo spreadsheet rỗng
        spreadsheet = (
            sheets_service.spreadsheets()
            .create(body={"properties": {"title": title}})
            .execute()
        )
        spreadsheet_id = spreadsheet["spreadsheetId"]

        # 2. Ghi dữ liệu vào sheet đầu tiên
        if data:
            body = {"values": data}
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A1",
                valueInputOption="RAW",
                body=body,
            ).execute()

        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"[Google Sheets] Đã tạo thành công: {sheet_url}")
        return f"✅ Đã xuất ra Google Sheets: {sheet_url}"

    except Exception as e:
        return f"[Google Sheets] Lỗi khi xuất: {e}"


def is_google_workspace_configured() -> bool:
    """Kiểm tra xem Google Workspace đã được cấu hình chưa."""
    return os.path.exists(CREDENTIALS_FILE) or os.path.exists(TOKEN_FILE)
