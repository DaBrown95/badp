-- Controlled CPU entry: descriptor association and initial busy flag are
-- injected, so these observations do not establish normal game reachability.
local cases={{0x1A,0},{0x1B,0},{0x1A,1}}
local saved=nil;local case=0;local active=false;local finished=false;local frames=0;local interrupts=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function physical(a)
 local m=emu.convertAddress(a,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom then return -1 end
 return m.address
end
local function setup()
 local c=cases[case+1]
 w(0x53,0xFC);w(0x54,0x6D);w(0x10,5);w(0x04E5,c[1]);w(0x0535,0);w(0x48,0x10);w(0xE7,c[2])
 w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 local cpu=emu.getCpuState();cpu.pc=0xD54E;emu.setCpuState(cpu);interrupts=0;active=true
end
local function finish(kind)
 print(string.format('RESULT %d %s %d',case,kind,interrupts))
 active=false;case=case+1
 if case==#cases then finished=true;print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(saved) then finished=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end
emu.addMemoryCallback(function()
 if finished then return end
 if not saved then
  if physical(0xFE6C)~=0x7E6C then return end
  saved=emu.createSavestate();setup();return
 end
 if active then
  local cpu=emu.getCpuState()
  print(string.format('FETCH %d %04X %02X %04X',case,r(0x53)+256*r(0x54),cpu.x,physical(0xFE6C)))
 end
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function()
 if active then
  local cpu=emu.getCpuState()
  if cpu.y==0 then
   local pointer=r(0x53)+256*r(0x54)
   print(string.format('COPY %d %04X %04X %02X',case,pointer,physical(pointer),cpu.x))
  end
 end
end,emu.callbackType.exec,0xFE90,0xFE90)
emu.addMemoryCallback(function()
 if active then print(string.format('DISPATCH %d %02X %02X %04X %04X %02X',case,r(0x60),r(0xFE),r(0x53)+256*r(0x54),physical(0xD57A),r(0xE7))) end
end,emu.callbackType.exec,0xD57A,0xD57A)
emu.addMemoryCallback(function() if active then interrupts=interrupts+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addMemoryCallback(function()
 if active then print(string.format('TARGET %d %04X',case,physical(0xA9D8)));finish('target') end
end,emu.callbackType.exec,0xA9D8,0xA9D8)
emu.addMemoryCallback(function()
 if active then print(string.format('WAIT %d %04X',case,physical(0xE1DD)));finish('wait') end
end,emu.callbackType.exec,0xE1DD,0xE1DD)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not finished then finished=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
