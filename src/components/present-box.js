const presentBoxComponent = {
  init() {
    this.el.sceneEl.addEventListener('transition-end', () => {
      setTimeout(this.spawnBox.bind(this), 5300)
    })
  },

  spawnBox() {
    const scene = document.querySelector('a-scene')

    const box = document.createElement('a-entity')
    box.setAttribute('id', 'presentBox')
    box.setAttribute('class', 'clickable')
    box.setAttribute('position', '0 -0.5 -6')

    // Box body
    const body = document.createElement('a-box')
    body.setAttribute('scale', '0.5 0.5 0.5')
    body.setAttribute('material', 'color: #D72638')
    box.appendChild(body)

    // Ribbon horizontal (runs along X axis)
    const ribH = document.createElement('a-box')
    ribH.setAttribute('scale', '0.52 0.06 0.06')
    ribH.setAttribute('position', '0 0 0')
    ribH.setAttribute('material', 'color: #FFD700')
    box.appendChild(ribH)

    // Ribbon vertical (runs along Z axis)
    const ribV = document.createElement('a-box')
    ribV.setAttribute('scale', '0.06 0.06 0.52')
    ribV.setAttribute('position', '0 0 0')
    ribV.setAttribute('material', 'color: #FFD700')
    box.appendChild(ribV)

    // Ribbon top (flat cross on lid)
    const ribTop = document.createElement('a-box')
    ribTop.setAttribute('scale', '0.52 0.06 0.52')
    ribTop.setAttribute('position', '0 0.28 0')
    ribTop.setAttribute('material', 'color: #FFD700')
    box.appendChild(ribTop)

    // Pop-up animation: rises from below ground to just above it
    box.setAttribute('animation', {
      property: 'position',
      from: '0 -0.5 -6',
      to: '0 0.5 -6',
      dur: 700,
      easing: 'easeOutElastic',
      delay: 0,
    })

    // Idle bob animation: gentle float after pop completes
    box.setAttribute('animation__bob', {
      property: 'position',
      from: '0 0.5 -6',
      to: '0 0.65 -6',
      dur: 1200,
      dir: 'alternate',
      loop: true,
      easing: 'easeInOutSine',
      delay: 700,
    })

    // Keep click for desktop; use touchend + manual raycast for 8th Wall mobile
    // (8th Wall's XR canvas intercepts touch events before A-Frame cursor can dispatch click)
    const showModal = () => {
      document.getElementById('giftModal').style.display = 'flex'
    }

    box.addEventListener('click', showModal)

    const onTap = (e) => {
      const touch = e.changedTouches[0]
      const cam = document.getElementById('camera').getObject3D('camera')
      const canvas = scene.canvas
      const rect = canvas.getBoundingClientRect()
      const x = ((touch.clientX - rect.left) / rect.width) * 2 - 1
      const y = -((touch.clientY - rect.top) / rect.height) * 2 + 1
      const raycaster = new THREE.Raycaster()
      raycaster.setFromCamera({x, y}, cam)
      if (raycaster.intersectObject(box.object3D, true).length > 0) {
        showModal()
      }
    }
    window.addEventListener('touchend', onTap)

    scene.appendChild(box)
  },
}

export {presentBoxComponent}
