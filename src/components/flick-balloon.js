const flickBalloonComponent = {
  init() {
    this.launched = false
    this.isDragging = false
    this.restY = -7
    this.currentY = -7
    this.springVelocity = 0
    this.touchHistory = []
    this.touchStartScreenY = 0
    this.touchStartWorldY = 0

    this.raycaster = new THREE.Raycaster()

    this._onTouchStart = this._onTouchStart.bind(this)
    this._onTouchMove = this._onTouchMove.bind(this)
    this._onTouchEnd = this._onTouchEnd.bind(this)

    const attachToCanvas = () => {
      const canvas = this.el.sceneEl.canvas
      if (!canvas) return
      canvas.addEventListener('touchstart', this._onTouchStart, {passive: false})
      canvas.addEventListener('touchmove',  this._onTouchMove,  {passive: false})
      canvas.addEventListener('touchend',   this._onTouchEnd)
    }
    if (this.el.sceneEl.renderer) {
      attachToCanvas()
    } else {
      this.el.sceneEl.addEventListener('renderstart', attachToCanvas, {once: true})
    }

    // Stop responding once launched via any mechanism (flick or natural sky detection)
    this.el.sceneEl.addEventListener('sky-coaching-overlay.hide', () => {
      this.launched = true
    })
  },

  _getNDC(touch) {
    const canvas = this.el.sceneEl.canvas
    const rect = canvas.getBoundingClientRect()
    return {
      x: ((touch.clientX - rect.left) / rect.width) * 2 - 1,
      y: -((touch.clientY - rect.top) / rect.height) * 2 + 1,
    }
  },

  _hitsBalloon(touch) {
    const cam = document.getElementById('camera').getObject3D('camera')
    if (!cam) return false
    const ndc = this._getNDC(touch)
    this.raycaster.setFromCamera(ndc, cam)
    return this.raycaster.intersectObject(this.el.object3D, true).length > 0
  },

  _onTouchStart(e) {
    if (this.launched) return
    const touch = e.touches[0]
    if (!this._hitsBalloon(touch)) return

    this.isDragging = true
    this.touchStartScreenY = touch.clientY
    this.touchStartWorldY = this.currentY
    this.springVelocity = 0
    this.touchHistory = [{y: touch.clientY, t: performance.now()}]
    e.preventDefault()
  },

  _onTouchMove(e) {
    if (!this.isDragging || this.launched) return
    e.preventDefault()

    const touch = e.touches[0]
    const deltaScreenY = this.touchStartScreenY - touch.clientY // positive = finger moved up
    const screenH = this.el.sceneEl.canvas.clientHeight || window.innerHeight
    const worldDelta = (deltaScreenY / screenH) * 18

    this.currentY = Math.max(this.restY - 1, Math.min(this.touchStartWorldY + worldDelta, 4))
    this.el.object3D.position.y = this.currentY

    const now = performance.now()
    this.touchHistory.push({y: touch.clientY, t: now})
    this.touchHistory = this.touchHistory.filter(p => now - p.t < 120)
  },

  _onTouchEnd() {
    if (!this.isDragging) return
    this.isDragging = false
    if (this.launched) return

    // px/ms, positive = finger moved up
    let flickVelocity = 0
    if (this.touchHistory.length >= 2) {
      const first = this.touchHistory[0]
      const last = this.touchHistory[this.touchHistory.length - 1]
      const dt = last.t - first.t
      if (dt > 0) flickVelocity = (first.y - last.y) / dt
    }

    if (flickVelocity > 0.7 || this.currentY > 0) {
      this._triggerLaunch()
    } else {
      // Convert screen velocity to world spring velocity so the balloon
      // continues upward a bit before floating back down
      this.springVelocity = flickVelocity * 8
    }
  },

  _triggerLaunch() {
    if (this.launched) return
    this.launched = true
    this.el.sceneEl.emit('sky-coaching-overlay.hide')
  },

  tick(t, delta) {
    if (this.launched || this.isDragging) return

    const dt = Math.min(delta, 50) / 1000 // seconds, capped

    // Spring back to restY with damping
    const spring = 10
    const damping = 0.88
    const displacement = this.currentY - this.restY

    this.springVelocity += -spring * displacement * dt
    this.springVelocity *= Math.pow(damping, dt * 60) // framerate-independent
    this.currentY += this.springVelocity * dt

    this.el.object3D.position.y = this.currentY
  },

  remove() {
    const canvas = this.el.sceneEl && this.el.sceneEl.canvas
    if (canvas) {
      canvas.removeEventListener('touchstart', this._onTouchStart)
      canvas.removeEventListener('touchmove', this._onTouchMove)
      canvas.removeEventListener('touchend', this._onTouchEnd)
    }
  },
}

export {flickBalloonComponent}
