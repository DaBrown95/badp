-- The runner supplies SCENARIO: 0 Noah, 1 Moses, 2 David.
-- Record mapped sprite resource and frame headers at their consuming routines.
local frames=0
local reads={frame={},header={}}
local missing={frame=0,header=0}
local calls={frame=0,header=0}
local function observe(kind,addr,phys)
 local q=emu.convertAddress(addr,emu.memType.nesMemory)
 if not q or q.memType~=emu.memType.nesPrgRom or q.address~=phys then return end
 calls[kind]=calls[kind]+1
 local p=emu.read(0xFE,emu.memType.nesDebug)+256*emu.read(0xFF,emu.memType.nesDebug)
 local m=emu.convertAddress(p,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or p>0xFFFE then missing[kind]=missing[kind]+1;return end
 local k=string.format('%04X:%02X%02X',m.address,emu.read(p,emu.memType.nesDebug),emu.read(p+1,emu.memType.nesDebug))
 reads[kind][k]=(reads[kind][k] or 0)+1
end
emu.addMemoryCallback(function() observe('header',0x880C,0x080C) end,emu.callbackType.exec,0x880C,0x880C)
emu.addMemoryCallback(function() observe('frame',0x8DF8,0x0DF8) end,emu.callbackType.exec,0x8DF8,0x8DF8)
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
  print('SPRITE_DONE 16000')
  for _,kind in ipairs({'frame','header'}) do
   print(string.format('SPRITE_TOTAL %s %d %d',kind,calls[kind],missing[kind]))
   for k,n in pairs(reads[kind]) do print(string.format('SPRITE_READ %s %s %d',kind,k,n)) end
  end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
