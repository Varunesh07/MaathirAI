import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const fetchMemory = async () => {
  try {
    const res = await api.get('/interactions/memory');
    return {
      ...res.data.medical_profile,
      interactions: res.data.interactions || []
    };
  } catch (err) {
    console.error("Error fetching memory:", err);
    return null;
  }
};

export const fetchChatHistory = async () => {
  try {
    const res = await api.get('/chat/');
    return res.data.chat_history;
  } catch (err) {
    console.error("Error fetching chat history:", err);
    return [];
  }
};

export const clearMemory = async () => {
  await api.delete('/interactions/memory');
};

export const uploadFile = async (file, message = null, skipExplanation = false) => {
  const formData = new FormData();
  formData.append('files', file); 
  if (message) {
    formData.append('message', message);
  }
  formData.append('skip_explanation', skipExplanation);
  const res = await api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const sendMessage = async (message) => {
  const res = await api.post('/chat/', { message });
  return res.data;
};
