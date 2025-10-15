export const getConfig = (key) => {
  return window.APP_CONFIG?.[key] || import.meta.env[key]
}