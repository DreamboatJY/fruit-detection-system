/**
 * 解析 JWT token 的 payload 部分
 * @param {string} token - JWT token 字符串
 * @returns {object|null} 解析后的 payload 对象，解析失败返回 null
 */
function parseToken(token) {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64Url = parts[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        })
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

/**
 * 检查当前 token 是否已过期
 * 优先通过 JWT 的 exp 字段判断，若无法解析则仅检查 token 是否存在
 * @returns {boolean} true 表示已过期或无效，false 表示有效
 */
export function isSessionExpired() {
  const token = localStorage.getItem('token')
  if (!token) return true

  const payload = parseToken(token)
  if (!payload) return true

  if (payload.exp) {
    const now = Math.floor(Date.now() / 1000)
    return payload.exp <= now
  }

  return false
}

/**
 * 清除所有登录态数据（localStorage + 预留 store 清理标记）
 */
export function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}
