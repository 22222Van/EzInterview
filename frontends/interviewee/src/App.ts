import { defineComponent, onMounted } from 'vue'

interface Student {
  name: string
  id: string
}

export default defineComponent({
  name: 'App',
  data() {
    return {
      student: {
        name: '张伟',
        id: '2023123456',
      } as Student,
      avatarUrl: 'https://i.pravatar.cc/1000' as string,
      answer: '' as string,
      volume: 50,
      micLevel: 70,
      networkQuality: '非常好' as string,
      questionContent: '' as string,
    }
  },
  mounted() {
    const host = window.location.hostname
    const port = '9009'
    const socket = new WebSocket(`ws://${host}:${port}/`)

    socket.onopen = () => {
      console.log(`WebSocket 已连接.`)
    }

    socket.onmessage = (event) => {
      console.log('收到题目:', event.data)
      this.questionContent = event.data
    }

    socket.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }

    socket.onclose = () => {
      console.log('WebSocket 连接关闭')
      this.questionContent = '错误：无法连接到后端。\n提示：你需要先启动后端再启动前端。'
    }
  },
})
