-- Inject $B3 inputs, then exercise the resulting voice commands. These cases
-- are controlled and do not establish that the slot values occur in play.
local cases={0x451B,0xC51B,0x451A,0x16A6,0x96A6,0x16A5,0x1365,0x5176,0x5178}
local saved=nil;local case=0;local phase=0;local reads=0;local interrupts=0;local frames=0;local finished=false
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a)
 local m=emu.convertAddress(a,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom then return -1 end
 return m.address
end
local function setup()
 local value=cases[case+1]
 w(0x10,5);w(0x75,value%256);w(0x85,math.floor(value/256));w(0x61,0xD0);w(0x62,0x26)
 w(0x53,0x34);w(0x54,0x12);w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 for i=0,4 do w(0x04B0+i*8,0) end
 reads=0;interrupts=0;phase=1
 local c=emu.getCpuState();c.pc=0xE967;c.x=5;emu.setCpuState(c)
end
local function finish()
 print(string.format('RESULT %d %d',case,interrupts));phase=0;case=case+1
 if case==#cases then finished=true;print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(saved) then finished=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end
emu.addMemoryCallback(function()
 if finished or saved or phys(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function()
 if phase==1 then
  local c=emu.getCpuState();local p=(r(0x53)+256*r(0x54)+c.y)%65536
  print(string.format('PAIR %d %04X %05X %02X',case,p,phys(p),r(p)))
 end
end,emu.callbackType.exec,0xFE90,0xFE90)
emu.addMemoryCallback(function()
 if phase~=1 then return end
 print(string.format('VOICE %d %02X %02X %02X %02X',case,r(0x04D0),r(0x04D1),r(0x04D4),r(0x04D5)))
 if case==2 or case==5 then finish();return end
 phase=2;local c=emu.getCpuState();c.pc=0x8FBA;emu.setCpuState(c)
end,emu.callbackType.exec,0xDF54,0xDF54)
emu.addMemoryCallback(function()
 if phase~=2 then return end
 local c=emu.getCpuState();local p=(r(0xFE)+256*r(0xFF)+c.y)%65536
 print(string.format('AUDIO %d %04X %05X %02X',case,p,phys(p),r(p)));reads=reads+1
end,emu.callbackType.exec,0xFEC3,0xFEC3)
emu.addMemoryCallback(function()
 if phase~=2 then return end
 local c=emu.getCpuState();if c.x~=0x20 then return end
 print(string.format('AFTER %d %d %02X %02X %02X %02X',case,reads,r(0x04D0),r(0x04D1),r(0x04D4),r(0x04D5)))
 if (case>=7 and reads==15) or (case<7 and reads==20) then finish();return end
 w(0x04D1,1);c.pc=0x8FBA;emu.setCpuState(c)
end,emu.callbackType.exec,0x8FD7,0x8FD7)
emu.addMemoryCallback(function() if phase>0 then interrupts=interrupts+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not finished then finished=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
