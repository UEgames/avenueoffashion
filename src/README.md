# A-Frame: Sky Effects + World Tracking

This A-Frame Sky Effects + World Tracking sample project showcases a modified sky coaching overlay, explains how to attach assets to the sky and world scenes, 
and illustrates how to transition assets from one scene to another.

![](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDc2OTM1ZjQyYTM5ZDdiYzc1MmNkZTA3OGVmY2IyOTE4MjEzODg0YSZjdD1n/qzqytGGAkfGMHWDsaR/giphy-downsized-large.gif)

For detailed documentation, visit the [Sky Effects + World Tracking Docs](https://www.8thwall.com/docs/api/aframe/#sky-effects) 🔗 

#### Sky Effects + World Tracking Overview

* components/
  * **animate-balloon.js** animates the balloon going up and over the foreground, utilizes the `transition-scene` component to transition the balloon from the Sky scene to the World scene.
  * **hide-overlay.js** adds functionality to the Sky Coaching Overlay to hide it once sky has been initially detected.
  * **recenter.js** recenters the Sky and World scenes automatically when sky is initially detected to ensure that the scene forward direction is the same as where sky was found.
  * **sky-remote-authoring.js** reconfigures your scene for sky effects desktop development and allows for remote authoring.
  * **transition-scene.js** transition the entity from the Sky Scene to the World Scene on attachment.
  * **sky-coaching-overlay** configures a sky coaching overlay to instruct users to look towards the sky when they are not looking at it. This component comes from the API 
  and can be added using `<meta name="8thwall:package" content="@8thwall.coaching-overlay">`

* assets/models/
  * **balloon.glb** low-poly hot air balloon
* assets/textures/
  * **foreground.svg** used by the `sky-remote-authoring` componenent to mimic foreground objects such as buildings and textures
  * **ground.svg** used by the `sky-remote-authoring` component to attach a grid-style texture to the ground

### *Developing Sky Effects + World Tracking Experiences*
Sky Effects + World Tracking is designed for experiences that incorporate sky segmentation and SLAM.

1. In your `<a-scene>` add the `xrlayers`, `xrweb`, and `xrconfig` components.
2. In your scene, add objects to the Sky scene using `<a-entity xrlayerscene="name:sky"></a-entity>` 
and add objects to the world scene by nesting them under `<a-scene></a-scene>`.
3. Transition objects from one scene to another using the `transition-scene` component and the `skyToSLAM` schema value.

Using Components for Sky Effects + World Tracking

* The `transition-scene` component will help you fluidly transition assets from the sky scene to the world scene or vice versa. It creates a new `<a-entity>` within the new scene
and reparents the asset you want to transition at the Object3D level. Use the schema value `direction` by setting it to `skyToSlam` if you are transitioning from the sky Scene to the world Scene
and set it to `slamToSky` if you are transitioning from the world scene to the sky scene. Use the `id` schema value to distinguish entities from one another from the event detail when transitioning multiple objects.

* The `sky-coaching-overlay` helps instruct users to find the sky in order to start the sky effects experience and is improved further by the `hide-overlay` component,
which permanently hides the coaching overlay once sky has been detected so that it doesn't show up in your world scene.

### *Remote Desktop Development Setup*
![](https://media.giphy.com/media/HyrfHNnj0UKpnDj7PM/giphy-downsized-large.gif)


It is often helpful to use the `sky-remote-authoring` component to position Sky Effects + World Tracking content remotely on your desktop. 
To set up this project's scene for remote desktop development, disable any components related to 8thWall's AR engine or mobile development
by adding a letter to the beginning (i.e. "Zxrlayers") or removing it altogether. The `sky-remote-authoring` component will automatically remove the following components:

- xrlayers
- xrweb
- xrconfig
- xrextras-loading
- xrextras-runtime-error
- landing-page
- sky-coaching-overlay

Next, add the `sky-remote-authoring` component to your <a-scene> element as last component in the list of attached components (after `xrlayers`).

Now you can open the Sky Effects + World Tracking scene and position content relative to the sky and ground through any desktop browser!

Additional Notes:
* An alternative to using the `sky-remote-authoring` component is to use a stock image of the sky ([example](https://wallpapercave.com/wp/wp2894344.jpg)) on a monitor.
* Toggle the foreground element using the schema value `foreground` on the `sky-remote-authoring` component.
* The `sky-remote-authoring` component will automatically reparent elements in your `<a-entity xrlayerscene="name:sky>` element to the `<a-scene>` for desktop development
* Ensure `sky-remote-authoring` is listed last/in the correct order on the <a-scene> element or else remote authoring may not work correctly.

### *Best Practices & Tips* 
* Ensure that there is a focal point within the sky scene so the user isn't overwhelmed by the contents; it's also helpful to create a leading line to guide your user's eyes using the motion of objects that transition from one scene to another.
* Ensure that lighting is the same between the sky Scene and the world scene. You will have to have the same number of lights in both scenes to ensure that objects look the same when transitioned from one to the other.
* GLB animations played using the aframe-extras `animation-mixer` component, will automatically continue playing after the transition when using the `transition-scene` component. 
* RGB Encoding and `colorManagement` is currently not supported in Sky Effects + World Tracking, we reccomend using `renderer="colorManagement:false'` to ensure consistent colors between both scenes.
* Ensure the z value of the transition point is less than 0 when transitioning from the sky scene to the world scene; if not, the object will appear behind you in the world scene once it has transitioned out of the sky scene.
* Ensure the y value of the transition point is a higher value if you are unsure of where your users will be opening the experience, if not, objects can appear to "clip" through the foreground as they transition from one scene to another.
* Try to not transition GLB models with children as it can cause significant lag and performance issues; instead, you can combine them into the same GLB file and use a component like [gltf-part] (https://github.com/supermedium/superframe/tree/master/components/gltf-part)
or write your own code to traverse the GLB in order to access handles to separate models.
* When animating models for the scene transition, either use a component like [animation] (https://aframe.io/docs/1.4.0/components/animation.html) 
and set explicit animations before and after the transition, or bake an animation within a GLB model and play it using `animation-mixer` before you transition the asset.
* Use the `edgeSmoothness` property of the `<a-entity xrlayerscene="name:sky>` element to feather the segmentation mask so that the edge between sky and not sky is more natural.
* Use the `invertLayerMask` property of the `<a-entity xrlayerscene="name:sky>` element to overlay everything but sky pixels within the sky scene.
* Additive and other Advanced Blending modes are currently not supported in the sky scene; instead, you can use a video texture with a lighter background, transparency, and with a lower opacity.
* Pin to Camera: Pin assets to the camera instead of to the world by nesting the whole `<a-entity xrlayerscene="name:sky">` element within the `<a-camera>` element or you can
append the camera to the `<a-entity xrlayerscene="name:sky">` element and append specific objects to the camera. 

### About Sky Effects + World Tracking
Sky Effects brings Niantic’s Sky Segmentation technology to the browser to identify and segment the sky, 
creating a canvas for AR content or for you to replace completely. 

World Tracking (sometimes referred to as World Effects) is the act of building the map or scene in front of the camera and relocalizing as the user moves. 
It is what allows for AR on the “Ground.” It is powered by 8th Wall’s proprietary SLAM engine, \
which is the first SLAM engine built for the web and optimized for real-time interaction in the browser. 
When launched, it helps a user quickly understand the scene by building a machine-readable representation of the physical world. 
It finds the flat plane, accounts for realistic lighting, and localizes / relocalizes the users. 

8th Wall developers can now simultaneously use Sky Effects + World Tracking, two powerful AR features, 
to fully augment the scene and create immersive, fantastical AR experiences - a first for any platform. 

### Asset Attribution
- Hot air balloon by Poly by Google [CC-BY] (https://creativecommons.org/licenses/by/3.0/) via [Poly Pizza] (https://poly.pizza/m/8azSIUgP0ow)