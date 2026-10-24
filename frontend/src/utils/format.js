import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export const formatTime = (value) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-')

export const formatDate = (value) => (value ? dayjs(value).format('YYYY-MM-DD') : '-')

export const fromNow = (value) => (value ? dayjs(value).fromNow() : '-')

export const TYPE_TEXT = { lost: '失物', found: '招领' }

export const ITEM_STATUS_TEXT = {
  published: '寻找中',
  returned: '已归还',
  offline: '已下架',
}

export const CLAIM_STATUS_TEXT = {
  pending: '待处理',
  approved: '已通过',
  rejected: '已拒绝',
  cancelled: '已撤销',
}

export const itemStatusType = (status) =>
  ({ published: 'primary', returned: 'success', offline: 'info' })[status] || 'info'

export const claimStatusType = (status) =>
  ({ pending: 'warning', approved: 'success', rejected: 'danger', cancelled: 'info' })[status] ||
  'info'

export const typeTagType = (type) => (type === 'lost' ? 'danger' : 'success')

/** 图片相对路径可以直接用，开发期由 vite 代理转发到后端 */
export const imageUrl = (path) => path || ''
