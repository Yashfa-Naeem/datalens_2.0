import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",  // ← /api added here
});

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload", formData);
  return response.data;
}

export async function getProfile(datasetId) {
  const response = await api.get(`/datasets/${datasetId}/profile`);
  return response.data;
}

export async function getData(datasetId, filters = {}) {
  const response = await api.get(`/datasets/${datasetId}/data`, { params: filters });
  return response.data;
}

export async function sendChatMessage(datasetId, message) {
  const response = await api.post(`/datasets/${datasetId}/chat`, { message });
  return response.data;
}

export async function getSummary(datasetId) {
  const response = await api.get(`/datasets/${datasetId}/summary`);
  return response.data;
}