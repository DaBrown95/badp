-- The runner supplies SCENARIO: 0 Noah, 1 Moses, 2 David.
-- The probe records five-byte audio command fetches after bank switching.
local frames=0
local pending=false
local crossings=0
local started=0
local completed=0
local overwritten=0
local audio={}
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0x8FF8,emu.memType.nesMemory)
 if m and m.memType==emu.memType.nesPrgRom and m.address==0x0FF8 then
  if pending then overwritten=overwritten+1 end
  pending=true
  started=started+1
 end
end,emu.callbackType.exec,0x8FF8,0x8FF8)
emu.addMemoryCallback(function()
 if pending then
  completed=completed+1
  local p=emu.read(0xFE,emu.memType.nesDebug)+256*emu.read(0xFF,emu.memType.nesDebug)
  local m=emu.convertAddress(p,emu.memType.nesMemory)
  if not m or m.memType~=emu.memType.nesPrgRom or p>0xFFFB then crossings=crossings+1
  else
   local bytes=''
   for i=0,4 do bytes=bytes..string.format('%02X',emu.read(p+i,emu.memType.nesDebug)) end
   local k=string.format('%04X:%s',m.address,bytes);audio[k]=(audio[k] or 0)+1
  end
  pending=false
 end
end,emu.callbackType.exec,0xFEC3,0xFEC3)
emu.addEventCallback(function()
 local move=frames>=180 and frames<185
 local start=(frames>=300 and frames<305) or (frames>=900 and frames<905)
 emu.setInput({up=move and SCENARIO==0,down=move and SCENARIO==2,
  left=frames>=1450 and ((frames-1450)%3600)>=1800 and ((frames-1450)%3600)<3300,
  right=frames>=1450 and ((frames-1450)%3600)<1700,start=start,select=false,
  a=frames>=1450 and ((frames-1450)%80)<12,
  b=frames>=1450 and ((frames-1450)%110)<12},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frames=frames+1
 if frames==16000 then
  print(string.format('AUDIO_DONE %d %d %d %d %d %d',frames,crossings,started,completed,overwritten,pending and 1 or 0))
  for k,n in pairs(audio) do print(string.format('AUDIO_READ %s %d',k,n)) end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
