import request from './request'

/**
 * 上传单张图片，返回 { url, filename }。
 * 注意不要手动设置 Content-Type，浏览器会自己带上 multipart 的 boundary。
 */
export const uploadImage = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/api/v1/upload/image', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
