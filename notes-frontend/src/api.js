const API_BASE_URL = 'http://127.0.0.1:8080';

// Вспомогательные функции
async function handleResponse(response) {
    if (!response.ok) {
        const text = await response.text(); // Получаем текст ошибки из тела ответа
        throw new Error(`HTTP error! Status: ${response.status}, Body: ${text}`);
    }
    try {
        return await response.json(); // Пытаемся распарсить как JSON
    } catch (e) {
        // Если не JSON, возвращаем текст
        return await response.text(); // или можно вернуть null, если не ожидается тело ответа
    }
}

async function getAccessToken() {
    return localStorage.getItem('accessToken');
}

async function getRefreshToken() {
    return localStorage.getItem('refreshToken');
}

async function setAccessToken(token) {
    localStorage.setItem('accessToken', token);
}

async function setRefreshToken(token) {
    localStorage.setItem('refreshToken', token);
}

async function clearTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
}

async function refreshToken() {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) {
        throw new Error('No refresh token available.');
    }

    const response = await fetch(`${API_BASE_URL}/user/refresh_tokens/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const data = await handleResponse(response);
    await setAccessToken(data.access_token);
    await setRefreshToken(data.refresh_token);
    return data.access_token;
}


// API Endpoints
const healthCheckNoteService = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/notes_service/health_check/`);
        return handleResponse(response);
    } catch (error) {
        console.error("Health check failed:", error);
        throw error;
    }
};

const healthCheckUserService = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/users_service/health_check/`);
        return handleResponse(response);
    } catch (error) {
        console.error("Health check failed:", error);
        throw error;
    }
};

const loginUser = async (username, password) => {
    try {
        console.info("Use username to fetch login", username)
        console.info("Use password to fetch login", password)

        const formData = new FormData();
        formData.append("grant_type", "password");
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}/user/login/`, {
            method: 'POST',
            body: formData
        });

        const data = await handleResponse(response);
        await clearTokens();
        await setAccessToken(data.access_token);
        await setRefreshToken(data.refresh_token); //Сохраняем refresh токен
        return data;
    } catch (error) {
        console.error("Login failed:", error);
        throw error;
    }
};

const registerUser = async (userData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/user/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        const data = await handleResponse(response);

        // Log in after successful registration
        await loginUser(userData.username, userData.password);

        return data;
    } catch (error) {
        console.error("Registration failed:", error);
        throw error;
    }
};


// //Автоматическое обновление токена (не вызывать напрямую, используется внутри)
// async function refreshToken() {
//     const refreshToken = localStorage.getItem('refreshToken');
//     if (!refreshToken) {
//         throw new Error('No refresh token available.');
//     }
//
//     const response = await fetch(`${API_BASE_URL}/user/refresh_tokens/`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ refresh_token: refreshToken }),
//     });
//
//     const data = await handleResponse(response);
//     localStorage.setItem('accessToken', data.access_token);
//     localStorage.setItem('refreshToken', data.refresh_token);
//     return data.access_token;
// }

const logoutUser = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/user/logout/`, {
            method: 'POST',
        });
        await clearTokens();
        return handleResponse(response);
    } catch (error) {
        console.error("Logout failed:", error);
        throw error;
    }
};

const getUserInfo = async () => {
    try {
        //Перед каждым запросом проверяем и обновляем токен
        const accessToken = await getAccessToken() || await refreshToken();
        const response = await fetch(`${API_BASE_URL}/user/self_info/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });
        return handleResponse(response);
    } catch (error) {
        console.error("Failed to fetch user info:", error);
        throw error;
    }
};

const createNote = async (title, content, files) => {
  try {
      const accessToken = await getAccessToken() || await refreshToken();
       //Разделяем файлы по типам
        const video_urls = files.filter(file => [".mp4", ".avi", ".webm"].some(ext => file.name.endsWith(ext)));
        const image_urls = files.filter(file => [".jpeg", ".jpg", ".png", ".webp"].some(ext => file.name.endsWith(ext)));
        const audio_urls = files.filter(file => [".mp3", ".ogg", ".wav"].some(ext => file.name.endsWith(ext)));

        const response = await fetch(`${API_BASE_URL}/notes/create/?title=${title}&content=${content}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({video_urls, image_urls, audio_urls}),
        });
        return handleResponse(response);
    } catch (error) {
        console.error("Failed to create note:", error);
        throw error;
    }
};

const deleteNote = async (noteId) => {
  try {
      const accessToken = await getAccessToken() || await refreshToken();
        const response = await fetch(`${API_BASE_URL}/notes/delete/${noteId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });
        return handleResponse(response);
    } catch (error) {
        console.error("Failed to delete note:", error);
        throw error;
    }
};

const getNotes = async () => {
  try {
      const accessToken = await getAccessToken() || await refreshToken();
        const response = await fetch(`${API_BASE_URL}/notes/get_notes/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });
        return handleResponse(response);
    } catch (error) {
        console.error("Failed to get notes:", error);
        throw error;
    }
};

export {
    healthCheckNoteService,
    healthCheckUserService,
    loginUser,
    registerUser,
    logoutUser,
    getUserInfo,
    createNote,
    deleteNote,
    getNotes,
    refreshToken
};
