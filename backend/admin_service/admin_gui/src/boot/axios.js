import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

export default boot(({ app, router }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !originalRequest.url.includes('/auth/refresh')
      ) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            failedQueue.push(() => resolve(api(originalRequest)))
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const response = await api.post('/auth/refresh', {}, { withCredentials: true })
          const newToken = response.data.access_token

          localStorage.setItem('access_token', newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`

          failedQueue.forEach((cb) => cb())
          failedQueue = []

          return api(originalRequest)
        } catch (refreshError) {
          failedQueue.forEach((cb) => cb())
          failedQueue = []
          localStorage.removeItem('access_token')

          router.push('/login')
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    },
  )
})

export function createAboutCard(formData) {
  return api.post('/about', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function loginUser(credentials) {
  const formData = new URLSearchParams()
  formData.append('email', credentials.email)
  formData.append('password', credentials.password)

  return api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export function logoutUser() {
  return api.post(
    '/auth/logout',
    {},
    {
      withCredentials: true,
    },
  )
}


// ABOUT
export function getAboutCardById(document_id) {
  return api.get(`/about/${document_id}`)
}

export function updateAboutText(document_id, textData) {
  const formData = new URLSearchParams()
  formData.append('title_en', textData.title_en)
  formData.append('description_en', textData.description_en)
  formData.append('title_ru', textData.title_ru)
  formData.append('description_ru', textData.description_ru)
  
  return api.patch(`/about/${document_id}`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function updateAboutImage(document_id, imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  
  return api.patch(`/about/${document_id}/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateTechSkills(kingdomName, skillsData) {
  return api.patch(`/technologies/${kingdomName}`, skillsData)
}

export function getProjects() {
  return api.get('/projects')
}

export function createProject(formData) {
  return api.post('/projects', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function deleteProject(documentId) {
  return api.delete(`/projects/${documentId}`)
}


export function getProjectById(documentId) {
  return api.get(`/projects/${documentId}`)
}

export function updateProjectText(documentId, textData) {
  const formData = new URLSearchParams()
  formData.append('title_en', textData.title_en)
  formData.append('title_ru', textData.title_ru)
  formData.append('description_en', textData.description_en)
  formData.append('description_ru', textData.description_ru)
  formData.append('link', textData.link)
  formData.append('popularity', textData.popularity.toString())
  
  return api.patch(`/projects/${documentId}`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function updateProjectImage(documentId, imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  
  return api.patch(`/projects/${documentId}/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// CERTIFICATES
export function getCertificates(sort = 'date_desc') {
  return api.get(`/certificates?sort=${sort}`)
}

export function getCertificateById(certificateId) {
  return api.get(`/certificates/${certificateId}`)
}

export function createCertificate(formData) {
  return api.post('/certificates', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateCertificateImage(certificateId, formData) {
  return api.patch(`/certificates/${certificateId}/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateCertificatePopularity(certificateId, popularity) {
  const formData = new URLSearchParams()
  formData.append('popularity', popularity.toString())
  
  return api.patch(`/certificates/${certificateId}`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function deleteCertificate(certificateId) {
  return api.delete(`/certificates/${certificateId}`)
}

// PUBLICATIONS
export function getPublications(lang = 'Each lang', sort = 'date_desc') {
  return api.get(`/publications?lang=${lang}&sort=${sort}`)
}

export function getPublicationById(documentId) {
  return api.get(`/publications/${documentId}`)
}

export function createPublication(publicationData) {
  const formData = new URLSearchParams()
  formData.append('title_en', publicationData.title_en)
  formData.append('title_ru', publicationData.title_ru)
  formData.append('page', publicationData.page)
  formData.append('site', publicationData.site)
  formData.append('rating', publicationData.rating.toString())
  formData.append('date', publicationData.date)

  return api.post('/publications', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function updatePublication(documentId, publicationData) {
  const formData = new URLSearchParams()
  formData.append('title_en', publicationData.title_en)
  formData.append('title_ru', publicationData.title_ru)
  formData.append('page', publicationData.page)
  formData.append('site', publicationData.site)
  formData.append('rating', publicationData.rating.toString())

  return api.patch(`/publications/${documentId}`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function deletePublication(documentId) {
  return api.delete(`/publications/${documentId}`)
}

// AUTH - User Management
export function getUsers() {
  return api.get('/auth')
}

export function registerUser(userData) {
  const formData = new URLSearchParams()
  formData.append('email', userData.email)
  formData.append('password', userData.password)
  
  // roles должен быть массивом строк
  if (userData.roles && userData.roles.length > 0) {
    userData.roles.forEach(role => {
      formData.append('roles', role)
    })
  }

  return api.post('/auth/register', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function updateUser(email, updateData) {
  const formData = new URLSearchParams()
  
  if (updateData.is_banned !== undefined) {
    formData.append('is_banned', updateData.is_banned.toString())
  }
  
  if (updateData.roles !== undefined) {
    // roles должен быть массивом строк
    updateData.roles.forEach(role => {
      formData.append('roles', role)
    })
  }

  return api.patch(`/auth/update/${email}`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function deleteUser(email) {
  const formData = new URLSearchParams()
  formData.append('email', email)

  console.log('Sending delete request for email:', email) // Лог для отладки

  return api.delete('/auth/delete', {
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// COMMENTS
export function getComments() {
  return api.get('/comments')
}

export function getCommentsByProjectId(projectId) {
  return api.get(`/comments/project/${projectId}`)
}

export function getCommentById(commentId) {
  return api.get(`/comments/${commentId}`)
}

export function createComment(commentData) {
  return api.post('/comments', commentData, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export function updateComment(commentId, updateData) {
  return api.patch(`/comments/${commentId}`, updateData, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export function deleteComment(commentId) {
  return api.delete(`/comments/${commentId}`)
}

export function banUserComments(authorId) {
  return api.patch(`/comments/ban_user/${authorId}`)
}



// NOTIFICATIONS
export function getNotifications() {
  return api.get('/notifications')
}

export function getNotificationsByEmail(email) {
  return api.get(`/notifications/by-email/${email}`)
}

export function deleteNotification(notificationId) {
  return api.delete(`/notifications/${notificationId}`)
}

export function createNotification(notificationData) {
  return api.post('/notifications', notificationData, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}



export { axios, api }
