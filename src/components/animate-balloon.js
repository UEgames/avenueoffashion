const animateBalloonComponent = {
  init() {
    let balloon
    const light = document.getElementById('light')

    const animate = () => {
      const pos = this.el.object3D.position
      this.el.setAttribute('animation', {
        property: 'position',
        from: `${pos.x.toFixed(3)} ${pos.y.toFixed(3)} ${pos.z.toFixed(3)}`,
        to: '0 10 -11',
        dur: 6000,
        delay: 0,
        easing: 'easeInOutQuad',
        loop: false,
      })
      this.el.setAttribute('animation__forward', {
        property: 'position',
        from: '0 10 -11',
        to: '0 8 -9',
        dur: 2000,
        delay: 6000,
        easing: 'easeInSine',
        loop: false,
      })

      // Slow continuous rotation in sky scene
      this.el.setAttribute('animation__rotate', {
        property: 'rotation',
        from: '0 0 0',
        to: '0 360 0',
        dur: 12000,
        easing: 'linear',
        loop: true,
      })

      this.el.sceneEl.addEventListener('transition-end', (event) => {
        balloon = event.detail.newEntity  // Grab the handle to the new Balloon Entity after it transitions from Sky Scene to World Scene
        balloon.setAttribute('id', 'newBalloon')
        balloon.setAttribute('shadow', {receive: true, cast: true})
        // Attach directional light to the new Balloon Entity to cast shadows
        light.setAttribute('xrextras-attach', {target: 'newBalloon'})
        light.setAttribute('light', {target: '#newBalloon'})

        // Animate the balloon from the transition point to the ground
        balloon.setAttribute('animation', {
          property: 'position',
          from: '0 8 -9',
          to: '0 0 -6',
          dur: 5000,
          delay: 0,
          easing: 'easeOutQuad',
          loop: false,
        })

        // Slow continuous rotation in world scene
        balloon.setAttribute('animation__rotate', {
          property: 'rotation',
          from: '0 0 0',
          to: '0 360 0',
          dur: 12000,
          easing: 'linear',
          loop: true,
        })
      })

      setTimeout(() => {
        this.el.setAttribute('transition-scene', {direction: 'skyToSlam', id: 'newBalloon'})  // Time transition with animation speeds
      }, 8000)

      // Animate Balloon when Sky is Found
      this.el.sceneEl.removeEventListener('sky-coaching-overlay.hide', animate)
    }
    this.el.sceneEl.addEventListener('sky-coaching-overlay.hide', animate)
  },
}
export {animateBalloonComponent}
