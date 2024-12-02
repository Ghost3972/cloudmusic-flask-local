<script setup>
  import QRCode from 'qrcode';
  import {onMounted, ref} from "vue";
  import { useRouter } from "vue-router";

  const qrcodeCanvas = ref(null)
  const qrcodeURL = ref("")
  const router  = useRouter();

  qrcodeURL.value = 'https://music.163.com/login?codekey=85576c46-6e16-43ca-a788-b6ec043b0766'
  const generateQRCode = () => {
    QRCode.toCanvas(qrcodeCanvas.value,qrcodeURL.value,function (error){
      if(error){
        console.log("qrcodeerror",error)
      } else {
        console.log("qrcodeok")
      }
    });
  };

  function redirectTest() {
    router.push('/login')
  }

  onMounted(() => {
    generateQRCode()
  })

</script>

<template>
  <div>
    <p>Home</p>
    <canvas ref="qrcodeCanvas"></canvas>
    <button @click="redirectTest">123</button>
  </div>
</template>

<style scoped>

</style>
