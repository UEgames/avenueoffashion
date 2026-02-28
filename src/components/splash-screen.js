const splashScreenComponent = {
  init() {
    const splash = document.getElementById('splashimage')
    const btn = document.getElementById('start')
    btn.style.display = 'block'
    btn.onclick = () => {
      this.el.sceneEl.setAttribute('xrweb', 'allowedDevices: any')
      splash.classList.add('hidden')
    }
  },
}
export { splashScreenComponent }
