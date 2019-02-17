# curveRig
Blender addon - Rig curve in one click
  
**[Download latest (2.8)](https://raw.githubusercontent.com/Pullusb/curveRig/master/curveRig.py)** (right click, save Target as)  

**[Download older (2.79)](https://raw.githubusercontent.com/Pullusb/curveRig/master/curveRig_279.py)** (right click, save Target as)

### Description:
Rig active curve to a new armature (or armature in selection) with bones envelopes on curve points and handlers


#### the curve
![base_curve](https://github.com/Pullusb/images_repo/raw/master/Bl_curveRig_base-curve.png)

#### one click later
![rigged](https://github.com/Pullusb/images_repo/raw/master/Bl_curveRig_rigged.png)

#### Perfect in combination with [Bone widget addon](https://github.com/ChristopheSeux/boneWidget) by [Christophe Seux](https://vimeo.com/user17486252) to make nice control shapes
![Bone_widget](https://github.com/Pullusb/images_repo/raw/master/Bl_curveRig_bone_widget.png)

#### Tadaaa
![result](https://github.com/Pullusb/images_repo/raw/master/Bl_curveRig_manipulate.png)


### Update:
  17/02/2079:
  - 2.8 version added as main version (older version renamed CurveRig_279)

  03/09/2017:
  - Change naming convention, better distinguish point and handler and allow prefix selection with shift+G in armature\_edit mode
    Points now prefixed 'PT', handlers 'CT' (previously all CT)

  07/07/2017:
  - Assign generated bones to a bone group for points and another for handlers with a color preset 
