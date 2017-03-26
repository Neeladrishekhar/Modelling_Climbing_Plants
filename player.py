import bge


def main():

    cont = bge.logic.getCurrentController()
    player = cont.owner
    
    kBoard = bge.logic.keyboard
    wKey = bge.logic.KX_INPUT_ACTIVE == kBoard.events[bge.events.WKEY]
    sKey = bge.logic.KX_INPUT_ACTIVE == kBoard.events[bge.events.SKEY]
    aKey = bge.logic.KX_INPUT_ACTIVE == kBoard.events[bge.events.AKEY]
    dKey = bge.logic.KX_INPUT_ACTIVE == kBoard.events[bge.events.DKEY]
    wKey_r = bge.logic.KX_INPUT_JUST_RELEASED == kBoard.events[bge.events.WKEY]

    mSpd = 0.1; rSpd = 0.05
    if wKey:
        player.applyMovement((0,mSpd,0), True)
    elif wKey_r:	# for drifting when we just released
        player.applyForce((0,5000*mSpd,0), True)

    if sKey:
        player.applyMovement((0,-mSpd,0), True)
    if aKey:
        player.applyRotation((0,0,rSpd), True)
    if dKey:
        player.applyRotation((0,0,-rSpd), True)

#    sens = cont.sensors['mySensor']
#    actu = cont.actuators['myActuator']

#    if sens.positive:
#        cont.activate(actu)
#    else:
#        cont.deactivate(actu)

main()
