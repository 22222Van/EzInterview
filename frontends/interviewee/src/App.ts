import { defineComponent } from 'vue'

// 定义类型接口
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
      networkQuality: '非常好'
    }
  },
})
