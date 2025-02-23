// frontend/src/App.vue
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Сервис шифрования и дешифрования</h1>

    <!-- Аутентификация -->
    <div v-if="!token" class="mb-6">
      <h2 class="text-xl mb-2">Вход</h2>
      <input v-model="username" placeholder="Логин" class="border p-2 w-full mb-2" />
      <input v-model="password" type="password" placeholder="Пароль" class="border p-2 w-full mb-2" />
      <button @click="login" class="bg-blue-500 text-white p-2 rounded">Войти</button>
      <p v-if="authError" class="text-red-500 mt-2">{{ authError }}</p>
    </div>

    <div v-if="token" class="absolute top-4 right-4">
      <button @click="logout" class="bg-red-500 text-white p-2 rounded">
        Выйти
      </button>
    </div>

    <!-- client credentials -->
    <div v-if="!token" class="mb-6">
      <h2 class="text-xl mb-2">Вход через Client Credentials</h2>
      <input v-model="clientId" placeholder="Client ID" class="border p-2 w-full mb-2" />
      <input v-model="clientSecret" type="password" placeholder="Client Secret" class="border p-2 w-full mb-2" />
      <button @click="getClientToken" class="bg-purple-500 text-white p-2 rounded">
        Получить токен
      </button>
    </div>

    <!-- Форма для текста -->
    <div class="mb-6" v-if="token">
      <h2 class="text-xl mb-2">Шифрование и дешифрование текста</h2>
      <input v-model="text" placeholder="Введите текст" class="border p-2 w-full mb-2" />
      <input v-model="key" placeholder="Введите ключ" class="border p-2 w-full mb-2" />
      <div class="flex gap-2">
        <button @click="encryptText" class="bg-blue-500 text-white p-2 rounded">Зашифровать</button>
        <button @click="decryptText" class="bg-green-500 text-white p-2 rounded">Расшифровать</button>
      </div>
      <p v-if="result" class="mt-4">Результат: {{ result }}</p>
    </div>

    <!-- Форма для файлов -->
    <div v-if="token">
      <h2 class="text-xl mb-2">Шифрование и дешифрование файлов</h2>
      <input type="file" @change="handleFile" class="mb-2" />
      <input v-model="fileKey" placeholder="Введите ключ" class="border p-2 w-full mb-2" />
      <div class="flex gap-2">
        <button @click="encryptFile" class="bg-blue-500 text-white p-2 rounded">Зашифровать файл</button>
        <button @click="decryptFile" class="bg-green-500 text-white p-2 rounded">Расшифровать файл</button>
      </div>
    </div>
    </div>
</template>

<script>
import axios from 'axios';
axios.defaults.baseURL = 'http://localhost:8000';

export default {
  created() {
      const savedToken = localStorage.getItem('token');
      if (savedToken) {
        this.token = savedToken;
      }
  },
  data() {
    return {
      username: '',
      password: '',
      token: '',
      authError: '',
      text: '',
      key: '',
      result: '',
      file: null,
      fileKey: ''
    };
  },
  methods: {
    async login() {
      try {
        const formData = new URLSearchParams();
        formData.append('username', this.username);
        formData.append('password', this.password);

        const response = await axios.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        this.token = response.data.access_token;
        localStorage.setItem('token', response.data.access_token);
        this.authError = '';
      } catch (error) {
        this.authError = 'Ошибка входа: неверные учетные данные';
      }
    },
    handleFile(event) {
      this.file = event.target.files[0];
    },
    async encryptText() {
      if (!this.text) {
        alert('Вставьте текст для шифрования!');
        return;
      }
      try {
        const formData = new FormData();
        formData.append('text', this.text);
        formData.append('key', this.key);
        const response = await axios.post('/encrypt/aes', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.token}` 
          }
        });
        if (response.data && response.data.encrypted_text) {
          this.result = response.data.encrypted_text;
        } else {
          throw new Error('Неверный формат ответа');
        }
      } catch (error) {
          if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          this.result = `Превышен лимит запросов. Попробуйте снова через ${retryAfter} секунд`;
          
          // Можно добавить автоматическую повторную попытку
          setTimeout(() => {
            this.encryptText();
          }, retryAfter * 1000);
        } else {
          this.result = 'Ошибка шифрования: ' + (error.response?.data?.detail || error.message);
        }
        this.result = 'Ошибка шифрования: ' + (error.response?.data?.detail || error.message);
      }
    },
    async decryptText() {
      try {
        const formData = new FormData();  // Изменить на FormData
        formData.append('text', this.text);
        formData.append('key', this.key);
        const response = await axios.post('/decrypt/aes', formData, {
          headers: { 
            'Content-Type': 'multipart/form-data',  // Добавить правильный Content-Type
            'Authorization': `Bearer ${this.token}` 
          }
        });
        this.result = response.data.decrypted_text;
      } catch (error) {
          if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          this.result = `Превышен лимит запросов. Попробуйте снова через ${retryAfter} секунд`;
          
          // Можно добавить автоматическую повторную попытку
          setTimeout(() => {
            this.decryptText();
          }, retryAfter * 1000);
        } else {
          this.result = 'Ошибка шифрования: ' + (error.response?.data?.detail || error.message);
        }
        this.result = 'Ошибка дешифрования';
      }
    },
    async encryptFile() {
      if (!this.file) {
      alert('Выберите файл для шифрования!');
      return;
    }
      try {
        const formData = new FormData();
        formData.append('file', this.file);
        formData.append('key', this.fileKey);
        formData.append('method', 'aes');
        const response = await axios.post('/encrypt/file', formData, {
          headers: { 
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.token}`,
          },
          responseType: 'blob'
        });
        console.log(response.data);
        this.downloadFile(response.data, response);
      } catch (error) {
        alert('Ошибка шифрования файла');
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          this.result = `Превышен лимит запросов. Попробуйте снова через ${retryAfter} секунд`;
          
          // Можно добавить автоматическую повторную попытку
          setTimeout(() => {
            this.encryptFile();
          }, retryAfter * 1000);
        } else {
          this.result = 'Ошибка шифрования: ' + (error.response?.data?.detail || error.message);
        }
      }
    },
    async decryptFile() {
      if (!this.file) {
      alert('Выберите файл для дешифрования!');
      return;
    }
      try {
        const formData = new FormData();
        formData.append('file', this.file);
        formData.append('key', this.fileKey);
        formData.append('method', 'aes')
        const response = await axios.post('/decrypt/file', formData, {
          headers: { 
            Authorization: `Bearer ${this.token}`,
            'Content-Type': 'multipart/form-data'
          },
          responseType: 'blob'
        });
        this.downloadFile(response.data, response);
      } catch (error) {
        alert('Ошибка дешифрования файла');
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          this.result = `Превышен лимит запросов. Попробуйте снова через ${retryAfter} секунд`;
          
          // Можно добавить автоматическую повторную попытку
          setTimeout(() => {
            this.decryptFile();
          }, retryAfter * 1000);
        } else {
          this.result = 'Ошибка шифрования: ' + (error.response?.data?.detail || error.message);
        }
      }
    },
    async logout() {
      try {
        await axios.post('/auth/logout', {}, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
        this.token = '';
        localStorage.removeItem('token');
        this.result = '';
        this.text = '';
        this.key = '';
        this.file = null;
        this.fileKey = '';
      } catch (error) {
        console.error('Ошибка при выходе:', error);
      }
    },

    async getClientToken() {
      try {
        const formData = new URLSearchParams();
        formData.append('client_id', this.clientId);
        formData.append('client_secret', this.clientSecret);
        formData.append('grant_type', 'client_credentials');

        const response = await axios.post('/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        this.token = response.data.access_token;
        localStorage.setItem('token', response.data.access_token);
        this.authError = '';
      } catch (error) {
        this.authError = 'Ошибка получения токена: неверные учетные данные';
      }
    },
    downloadFile(blob, response) {
      const contentDisposition = response.headers['content-disposition'];
  
      let filename = 'decrypted_file';

      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="?([^"]+)"?/);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }

      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      },
      
    }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background: linear-gradient(135deg, #1e1e1e, #2c2c2c);
  color: #e0e0e0;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.wrapper {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: start;
}

.container {
  background: #1a1a1a;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  max-width: 800px;
  width: 100%;
}

input, button {
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
}

input {
  background: #2b2b2b;
  color: #fff;
  border: 1px solid #3c3c3c;
  outline: none;
  margin-right: 5px;
  width: 300px;
  height: 50px;
}

input::placeholder {
  color: #888;
}

button {
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

button.bg-blue-500 {
  background: #3b82f6;
  color: #fff;
}

button.bg-blue-500:hover {
  background: #2563eb;
}

button.bg-green-500 {
  background: #10b981;
  color: #fff;
}

button.bg-green-500:hover {
  background: #059669;
}

h1, h2 {
  margin-bottom: 1rem;
}

h1 {
  font-size: 2rem;
  font-weight: 800;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
}

p {
  font-size: 1rem;
  line-height: 1.5;
}

.bg-red-500 {
  background: #ef4444;
}

.bg-red-500:hover {
  background: #dc2626;
}

.bg-purple-500 {
  background: #8b5cf6;
}

.bg-purple-500:hover {
  background: #7c3aed;
}

.absolute {
  position: absolute;
}

.top-4 {
  top: 1rem;
}

.right-4 {
  right: 1rem;
}

.text-red-500 {
  color: #ef4444;
}

.mt-4 {
  margin-top: 1rem;
}

.flex {
  display: flex;
}

.gap-2 {
  gap: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

/* Анимации для появления и исчезновения окон */
.fade-out {
  opacity: 0;
  transform: translateY(-20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
  pointer-events: none;
}

.fade-in {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.hidden {
  display: none;
}

/* Стили для скроллбара */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1e1e1e;
}

::-webkit-scrollbar-thumb {
  background: #3c3c3c;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

</style>
