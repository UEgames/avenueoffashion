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

    box.setAttribute('gltf-model', '#present2')
    box.setAttribute('scale', '1.5 1.5 1.5')

    // Pop-up animation: rises from below ground, lands at basket level
    box.setAttribute('animation', {
      property: 'position',
      from: '0 -0.5 -6',
      to: '0 0.15 -6',
      dur: 700,
      easing: 'easeOutElastic',
      delay: 0,
    })

    // Idle bob: dips low into basket so top/bow is visible, then rises clear
    box.setAttribute('animation__bob', {
      property: 'position',
      from: '0 0.15 -6',
      to: '0 0.75 -6',
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
