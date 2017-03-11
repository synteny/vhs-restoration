SOURCEVIDEO=FFVideoSource("%INPUT%").bilinearresize(400,480)


loss=imagesource("mask\hsync_%03d.bmp",end=127).assumefps(2997,100).loop(-1)

original=converttorgb32(sourcevideo).LEVELS(0,1,255,4,200).changefps(2997,100)


#0== GREYSCALE ==#

grey1=greyscale(original).bilinearresize(288,480).blur(-1,1).bicubicresize(400,480)
grey2=pointresize(grey1,800,480).crop(0,0,799,480).addborders(1,0,0,0).bilinearresize(400,480)

hsyncloss1=mergeARGB(showgreen(loss),showblue(loss),showblue(loss),showblue(loss)).pointresize(400,480)
hsyncloss2=invert(hsyncloss1,"A")
greysync1=layer(grey1,hsyncloss1)
greysync2=layer(grey2,hsyncloss2)
grey=overlay(greysync1,greysync2,mode="add",opacity=1).converttoyv12


#== COLOR ==#

#ADDBORDERS: How off-set is the chroma channel from luma (X,Y,0,0) X=Horizontally, Y=Vertically (Both Even Number)
colorinputu=original.bilinearresize(100,480).blur(1,0).bilinearresize(400,480).ADDBORDERS(4,2,0,0)

#For NTSC color (Hue Tinting)
colorinputv=converttoyv12(colorinputu).coloryuv(cont_v=-160).converttorgb32

#For PAL  color (No Tinting, removes blue tint)
#colorinputv=colorinputu


colorlossu=mergeARGB(showred(loss),showblue(loss),showblue(loss),showblue(loss)).pointresize(400,480)
colorlossv=trim(colorlossu,32,0)

coloru=layer(colorinputu,colorlossu).converttoyv12
colorv=layer(colorinputv,colorlossv).converttoyv12
color=mergechroma(coloru,colorv,0.5).coloryuv(gain_y=-256, cont_u=128, cont_v=128)

noise=ffvideosource("%NOISE%")
noise = noise.trim(rand(noise.FrameCount()),0).bilinearresize(400,480).loop(-1)
finalsignal=overlay(grey, color, mode="add", opacity=1)
overlay(finalsignal, noise, mode="add", opacity=1).LEVELS(40,1,255,0,255).SelectRangeEvery(125, %N%)
