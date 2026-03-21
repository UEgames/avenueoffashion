// If iOS Safari restores this page from the back/forward cache (bfcache),
// the XR session would resume in a broken state. Force a clean reload instead.
window.addEventListener('pageshow', (e) => {
  if (e.persisted) window.location.reload()
})

// Stop the camera before the page unloads so iOS doesn't show the
// "This page was using your camera — allow it to continue?" prompt on refresh.
// That prompt appears before JS runs and before the user can tap the button,
// and if dismissed it blocks camera permission for the whole session.
window.addEventListener('pagehide', () => {
  if (window.XR8) {
    try { XR8.stop() } catch (_) {}
  }
  // Also stop any live media tracks directly so iOS sees the camera as released.
  document.querySelectorAll('video').forEach((v) => {
    if (v.srcObject) {
      v.srcObject.getTracks().forEach((t) => t.stop())
    }
  })
})

const splashScreenComponent = {
  init() {
    const splash = document.getElementById('splashimage')
    const btn = document.getElementById('start')
    btn.style.display = 'block'
    btn.onclick = () => {
      this.el.sceneEl.setAttribute('xrweb', 'allowedDevices: any')
      this.el.sceneEl.setAttribute('xrlayers', '')
      splash.classList.add('hidden')
    }
  },
}
export { splashScreenComponent }
