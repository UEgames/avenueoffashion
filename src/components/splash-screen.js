const splashScreenComponent = {
  init() {
    const splash = document.getElementById('splashimage')
    const btn = document.getElementById('start')
    btn.style.display = 'block'

    // Guard against premature XR8.run() calls (e.g. from xrconfig/xrlayers on
    // cache-fast refresh). Swallow any call until the user taps Start AR.
    const guardXR = () => {
      const origRun = XR8.run
      XR8.run = (opts) => {
        if (this._started) {
          XR8.run = origRun  // restore before calling so XR8.run === origRun
          XR8.run(opts)
        }
      }
    }

    if (typeof XR8 !== 'undefined') {
      guardXR()
    } else {
      window.addEventListener('xrloaded', guardXR, {once: true})
    }

    btn.onclick = () => {
      this._started = true
      this.el.sceneEl.setAttribute('xrweb', 'allowedDevices: any')
      splash.classList.add('hidden')
    }
  },
}
export { splashScreenComponent }
