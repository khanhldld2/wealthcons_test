import os

# Cấu hình thư mục upload
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

# Cấu hình kết nối database
DATABASE_URL = "postgresql+psycopg2://username:password@localhost/database"
