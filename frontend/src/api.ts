
const API_BASE_URL = "http://127.0.0.1:5000/api/v1";

export interface LogFile {
  id: number;
  filename: string;
  total_lines: number;
  parsed_lines: number;
  failed_lines: number;
  uploaded_at: string;
}

export interface LogEntry {
  id: number;
  timestamp: string | null;
  level: string;
  source: string | null;
  message: string;
  line_number: number;
}

export interface FileEntriesResponse {
  file_id: number;
  filename: string;
  total_entries: number;
  entries: LogEntry[];
}

export async function fetchFiles(): Promise<LogFile[]> {
  const response = await fetch(`${API_BASE_URL}/files`);

  if (!response.ok) {
    throw new Error(`Failed to fetch files: ${response.status}`);
  }

  const data: { files: LogFile[] } = await response.json();
  return data.files;
}

export async function fetchFileEntries(
  fileId: number
): Promise<FileEntriesResponse> {
  const response = await fetch(
    `${API_BASE_URL}/files/${fileId}/entries`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch log entries: ${response.status}`);
  }

  return response.json();
}

export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/files`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error ?? `Upload failed: ${response.status}`);
  }

  return response.json();
}


export async function deleteFile(fileId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error ?? `Delete failed: ${response.status}`);
  }
}
