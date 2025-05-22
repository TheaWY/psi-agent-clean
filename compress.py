import zipfile
import os

# 압축할 폴더 경로
folder_to_zip = "C:/Users/LGCNS/Desktop/code/psi_agent_system_gpt_only_final_complete"

# 압축 파일이 저장될 경로 (파일명까지 포함)
zip_path = "C:/Users/LGCNS/Desktop/code/psi_agent_system_gpt_only_final_complete.zip"

def zip_folder(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(folder_path))  # 상대 경로로 저장
                zipf.write(abs_path, arcname=rel_path)

zip_folder(folder_to_zip, zip_path)
print("압축 완료:", zip_path)
