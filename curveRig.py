bl_info = {
    "name": "Curve rig",
    "description": "Add bones to control active curve with bone envelope",
    "author": "Samuel Bernou, Christophe Seux",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Tool Shelf > RIG tool > Curve rig",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }
    

import bpy
from bpy import context as C
from bpy import data as D
from mathutils import Vector
from math import sqrt

###Select an armature and a curve (curve must be active object)

def CreateArmatureModifier(ob, ArmatureObject):
    '''
    Create armature modifier if necessary and place it on top of stack
    or just after the first miror modifier
    return a list of bypassed objects
    '''

    #add armature modifier that points to designated rig:
    if not 'ARMATURE' in [m.type for m in ob.modifiers]:
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = ArmatureObject

        #bring Armature modifier to the top of the stack
        pos = 1
        if 'MIRROR' in [m.type for m in ob.modifiers]:
            #if mirror, determine it's position
            for mod in ob.modifiers:
                if mod.type == 'MIRROR':
                    pos += 1
                    break
                else:
                    pos += 1

        if len(ob.modifiers) > 1:
            for i in range(len(ob.modifiers) - pos):
                bpy.ops.object.modifier_move_up(modifier="Armature")

    else: #armature already exist
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                m.object = ArmatureObject
    #check use envelope and actevate influence
    for m in ob.modifiers:
        if m.type == 'ARMATURE':
            m.use_apply_on_spline = 1
            m.use_bone_envelopes = 1

def VectorLength(A,B):
    ''''take two Vector and return length'''
    return sqrt((A[0] - B[0])**2 + (A[1] - B[1])**2 + (A[2] - B[2])**2)

def VectorLengthCoeff(size, A, B):
    '''
    Calculate the vector lenght
    return the coefficient to multiply this vector
    to obtain a vector of the size given in paramerter
    '''
    Vlength = sqrt((A[0] - B[0])**2 + (A[1] - B[1])**2 + (A[2] - B[2])**2)
    return (size / Vlength)


def CrossVectorCoord(foo, bar, size):
    '''Return the coord in space of a cross vector between the two point with specified size'''
    ###middle location between 2 vector is calculated by adding the two vector and divide by two
    ##mid = (foo + bar) / 2
    between = foo - bar
    #create a generic Up vector (on Y or Z)
    up = Vector([0,1.0,0])
    #the cross product return a 90 degree Vector
    new = Vector.cross(up, between)
    perpendicular = foo + new
    coeff = VectorLengthCoeff(size, foo, perpendicular)
    #position the point in space by adding the new vector multiplied by coeff value to get wanted lenght
    return (foo + (new * coeff))


def midpoint(p1, p2):
    return (Vector([(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2]))


def setEnvelope(bone):
    bone.envelope_distance = 0.1
    bone.envelope_weight = 1.000
    bone.head_radius = 0.01
    bone.tail_radius = 0.0001


###---main function

def PlaceCurveControlBone(context):
    C = context
    
    #boneheight size of curve point
    boneheight = context.scene.RC_pointSize
    #handlerHeight size of handler bones
    handlerheight = context.scene.RC_handlerSize
    #automatic mode
    if context.scene.RC_CustomSize:
        auto = False
    else:
        auto = True

    ob = C.object
    mat = ob.matrix_world
    spcount = 0
    ptcount = 0
    selcount = 0

    ##obsolete with button greyed out
    if ob.type != 'CURVE':
        return (1, 'active object must be a curve !')

    armcount = 0
    arm = 0
    if C.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    for o in C.selected_objects:
        if o.type == 'ARMATURE':
            armcount = 1
            arm = o

    if not armcount:
        #create a new armature
        amt = bpy.data.armatures.new(ob.name + '_armature')
        obarm = bpy.data.objects.new(ob.name + '_rig', amt)
        C.scene.objects.link(obarm)
        #scn.objects.active = obarm
        obarm.select = True
        arm = obarm

    points = {}

    for spline in ob.data.splines:
        spcount += 1
        for pt in spline.bezier_points:
            ptcount += 1
            if pt.select_control_point or not context.scene.RC_SelectedOnly:
                selcount += 1
                name = 'CT' + str(spcount).zfill(2) + '_' + str(ptcount).zfill(2)
                loc = ob.matrix_world * pt.co
                points[name] = [mat * pt.co, mat * pt.handle_left.xyz, mat * pt.handle_right.xyz]

    if not selcount and context.scene.RC_SelectedOnly:
        return (1, 'No curve points selected.\nSelect points (not handlers !) in curve edit mode or uncheck "only selected curve points"')

    #Bone creation
    C.scene.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    edit_bones = arm.data.edit_bones

    for p, c in points.items():
        print("point", p)
        #create bones at point
        #print(p, c)
        b = edit_bones.new(p)
        phead = c[0]
        ##place center bone tail at 90 angle (according to tilt value ?)
        ###ptail = [c[0][0], c[0][1], c[0][2] + boneheight] #same as head with Z offset (handle lenght)

        if auto:
            #if automatic point bone size - height is 3/4 of right handler size
            boneheight =  VectorLength(c[0], c[2]) * 0.75
        ptail = CrossVectorCoord(c[0], c[1], boneheight)

        b.head = phead
        b.tail = ptail
        setEnvelope(b)
        #create bones at handle left...
        bl = edit_bones.new(p + '_L')

        bl.head = c[1]

        if auto:
            handlerheight = VectorLength(c[0], c[2]) * 0.4
        bl.tail = c[1] + ((c[1] - c[0]) * VectorLengthCoeff(handlerheight, c[1], c[0]))
        #bl.tail = c[1] + (c[1] - midpoint(c[1], phead) )
        bl.parent = b

        #...and right
        br = edit_bones.new(p + '_R')

        br.head = c[2]
        br.tail = c[2] + ((c[2] - c[0]) * VectorLengthCoeff(handlerheight, c[2], c[0]))
        ##br.tail = c[2] + (c[2] - midpoint(c[2], phead) )
        br.parent = b

    #return to object mode
    # exit edit mode to save bones so they can be used in pose mode
    bpy.ops.object.mode_set(mode='OBJECT')

    C.scene.objects.active = ob
    CreateArmatureModifier(ob, arm)
    if armcount:
        message = 'Bones added to ' + arm.name + ' rig'
        return (0, message)
    else:
        return (0, '')


###---operator and pannel

class curveArmatureOps(bpy.types.Operator):
    bl_idname = "rig.curve_rig"
    bl_label = "rig curve"
    bl_description = "Rig the curve, add bones (to selected armature) on controls points of the Curve"
    bl_options = {"REGISTER"}

    #@classmethod
    #def poll(cls, context):
    #    return True

    def execute(self, context):
        error, mess = PlaceCurveControlBone(context)
        if error:
            self.report({'ERROR'}, mess)
        else:
            if mess:
                self.report({'INFO'}, mess)
                
        return {"FINISHED"}


class CurveRigPanel(bpy.types.Panel):
    bl_idname = "curve_rig"
    bl_label = "Curve rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "RIG Tools"

    bpy.types.Scene.RC_SelectedOnly = bpy.props.BoolProperty(name = 'selectionOnly', default=True, description = "add bones only on selected point curve")
    bpy.types.Scene.RC_CustomSize = bpy.props.BoolProperty(name = 'CustomSize', default=False, description = "If not selected, bone sized individually according to handlers distance to control point")
    bpy.types.Scene.RC_pointSize = bpy.props.FloatProperty(name = 'boneCurvePoint', default=0.2, description = "size of the bone that control points of the curve")
    bpy.types.Scene.RC_handlerSize = bpy.props.FloatProperty(name = 'bonePointHandler', default=0.1, description = "size of the bone that control handlers of the points")

    
    def draw(self, context):
        layout = self.layout
        row = layout.row(align = 0)
        if context.object and context.object.type == 'CURVE':
            row.enabled = True
        else:
            row.enabled = False
        row.operator("rig.curve_rig",text= "Rig Curve")
        row = layout.row(align = 0)
        row.prop(context.scene, "RC_SelectedOnly", text="only selected curve points")

        row = layout.row(align = 0)
        row.prop(context.scene, "RC_CustomSize", text="manual bones sizes")        
        if context.scene.RC_CustomSize:
            row = layout.row(align = 0)
            row.prop(context.scene, "RC_pointSize", text="points bones size")
            row = layout.row(align = 0)
            row.prop(context.scene, "RC_handlerSize", text="handlers bones size")


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()