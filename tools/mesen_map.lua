-- The runner supplies SCENARIO: 0 Noah, 1 Moses, 2 David.
-- Pair map layout and tile/attribute span pointers with the mapped PRG bank.
local pending={layout=nil,row=nil,column=nil}
local started={layout=0,row=0,column=0}
local checked={layout=0,row=0,column=0}
local errors=0
local paired={}
local function start(kind,p)
 if pending[kind] then errors=errors+1 end
 local bank
 if p>=0x8000 then
  local m=emu.convertAddress(p,emu.memType.nesMemory)
  if not m or m.memType~=emu.memType.nesPrgRom then errors=errors+1;return end
  bank=math.floor(m.address/0x8000)
 else bank=emu.read(0x03C2,emu.memType.nesDebug)%2 end
 pending[kind]={pointer=p,bank=bank,state=emu.read(1,emu.memType.nesDebug)};started[kind]=started[kind]+1
end
local function code(addr,expected)
 local m=emu.convertAddress(addr,emu.memType.nesMemory)
 return m and m.memType==emu.memType.nesPrgRom and m.address==expected
end
emu.addMemoryCallback(function()
 if code(0x85E8,0x05E8) then start('layout',emu.read(0xF4,emu.memType.nesDebug)+256*emu.read(0xF5,emu.memType.nesDebug)) end
end,emu.callbackType.exec,0x85E8,0x85E8)
emu.addMemoryCallback(function()
 if code(0x98F1,0x18F1) then start('row',emu.read(0xF6,emu.memType.nesDebug)+256*emu.read(0xF7,emu.memType.nesDebug)) end
end,emu.callbackType.exec,0x98F1,0x98F1)
emu.addMemoryCallback(function()
 if code(0x9BF7,0x1BF7) then start('column',emu.read(0xF6,emu.memType.nesDebug)+256*emu.read(0xF7,emu.memType.nesDebug)) end
end,emu.callbackType.exec,0x9BF7,0x9BF7)
local function check(kind,lo,hi)
 local v=pending[kind];if not v then return end
 local cpu=emu.read(lo,emu.memType.nesDebug)+256*emu.read(hi,emu.memType.nesDebug)
 local wanted=(v.pointer%0x8000)+0x8000
 if cpu~=wanted then errors=errors+1;pending[kind]=nil;return end
 local m=emu.convertAddress(cpu,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=v.bank*0x8000+(wanted-0x8000) then errors=errors+1 end
 local k=string.format('%s:%04X:%d:%02X',kind,v.pointer,v.bank,v.state);paired[k]=(paired[k] or 0)+1
 checked[kind]=checked[kind]+1;pending[kind]=nil
end
emu.addMemoryCallback(function() check('layout',0xFE,0xFF) end,emu.callbackType.exec,0xFEC3,0xFEC3)
emu.addMemoryCallback(function() check('row',0xF6,0xF7) end,emu.callbackType.exec,0xFF58,0xFF58)
emu.addMemoryCallback(function() check('column',0xF6,0xF7) end,emu.callbackType.exec,0xFEF0,0xFEF0)
local frames=0
emu.addEventCallback(function()
 local move=frames>=180 and frames<185
 local start=(frames>=300 and frames<305) or (frames>=900 and frames<905)
 emu.setInput({up=(move and SCENARIO==0) or (frames>=1450 and ((frames-1450)%400)<75),
  down=(move and SCENARIO==2) or (frames>=1450 and ((frames-1450)%1200)>=1100 and ((frames-1450)%1200)<1130),
  left=frames>=1450 and ((frames-1450)%3600)>=1800 and ((frames-1450)%3600)<3300,
  right=frames>=1450 and ((frames-1450)%3600)<1700,start=start,
  select=(frames>=8000 and frames<8005) or (frames>=8400 and frames<8405),
  a=frames>=1450 and ((frames-1450)%80)<12,
  b=frames>=1450 and ((frames-1450)%130)<12},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frames=frames+1
 if frames==16000 then
  print('MAP_DONE 16000')
  for _,k in ipairs({'layout','row','column'}) do
   print(string.format('MAP_TOTAL %s %d %d %d',k,started[k],checked[k],pending[k] and 1 or 0))
  end
  print(string.format('MAP_ERRORS %d',errors))
  for k,n in pairs(paired) do print(string.format('MAP_DATA %s %d',k,n)) end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
