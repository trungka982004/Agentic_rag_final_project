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
    "https://www.googleapis.com/auth/drive.file",
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
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            return creds
        except Exception as e:
            creds = None

    if not creds:
        if not os.path.exists(CREDENTIALS_FILE):
            return None
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=OAUTH_CALLBACK_PORT, prompt="consent", open_browser=True)
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        except Exception:
            return None

    return creds


def upload_image_to_drive(file_path: str) -> str | None:
    """Uploads an image to Google Drive and returns a public URL."""
    creds = _get_google_credentials()
    if not creds: return None
    
    try:
        from googleapiclient.http import MediaFileUpload
        service = build("drive", "v3", credentials=creds)
        
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='image/png')
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webContentLink').execute()
        file_id = file.get('id')
        print(f"[Google Drive] File uploaded with ID: {file_id}")
        
        # Make file public so Google Docs can pull it (required for insertInlineImage)
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        # Get the direct download link
        file = service.files().get(fileId=file_id, fields='webContentLink').execute()
        link = file.get('webContentLink')
        print(f"[Google Drive] Public Link generated: {link}")
        return link
    except Exception as e:
        print(f"[Google Drive] Error: {e}")
        return None


def export_to_google_docs(title: str, content: str, image_urls: list[str] = None) -> str:
    """
    Tạo một Google Docs mới, ghi nội dung và chèn ảnh nếu có.
    """
    creds = _get_google_credentials()
    if not creds:
        return "[Google Workspace] Chưa cấu hình credentials."

    try:
        docs_service = build("docs", "v1", credentials=creds)
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
        
        # Insert images at the end if provided
        if image_urls:
            print(f"[Google Docs] Inserting {len(image_urls)} images...")
            for i, url in enumerate(image_urls):
                requests.append({
                    "insertInlineImage": {
                        "location": {"index": len(content) + 1 + i}, # Offset by i to avoid overlap
                        "uri": url,
                        "objectSize": {"height": {"magnitude": 400, "unit": "PT"}}
                    }
                })

        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
        print(f"[Google Docs] Batch update successful for {doc_id}")
        return f"✅ Đã xuất ra Google Docs: https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e:
        print(f"[Google Docs] Batch update error: {e}")
        return f"[Google Docs] Lỗi: {e}"


def export_to_google_sheets(title: str, data: list[list]) -> str:
    """
    Tạo một Google Sheets mới và ghi dữ liệu dạng bảng vào đó.
    """
    creds = _get_google_credentials()
    if not creds: return "[Google Workspace] Lỗi credentials."

    try:
        sheets_service = build("sheets", "v4", credentials=creds)
        spreadsheet = sheets_service.spreadsheets().create(body={"properties": {"title": title}}).execute()
        spreadsheet_id = spreadsheet["spreadsheetId"]

        if data:
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range="Sheet1!A1",
                valueInputOption="RAW", body={"values": data}
            ).execute()

        return f"✅ Đã xuất ra Google Sheets: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    except Exception as e:
        return f"[Google Sheets] Lỗi: {e}"


def is_google_workspace_configured() -> bool:
    return os.path.exists(CREDENTIALS_FILE) or os.path.exists(TOKEN_FILE)
