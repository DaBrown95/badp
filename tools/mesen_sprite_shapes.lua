-- Each case injects one observed frame pointer at the dimension routine.
-- This checks those reads, not gameplay reachability or physical wiring.
local cases={{FRAME_CASES}}
local saved=nil;local case=0;local reads=0;local bad=0;local interrupts=0;local frames=0;local done=false
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a)
 local m=emu.convertAddress(a,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom then return -1 end
 return m.address
end
local function setup()
 local p=cases[case+1];w(0xFE,p%256);w(0xFF,math.floor(p/256));w(0x03E2,0xA5);w(0x03E3,0xA5)
 w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 local c=emu.getCpuState();c.pc=0x8DF8;emu.setCpuState(c);reads=0;bad=0;interrupts=0
end
emu.addMemoryCallback(function()
 if saved or done or phys(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
local function record()
 if not saved or done then return end
 local c=emu.getCpuState();local p=r(0xFE)+256*r(0xFF)
 if p~=cases[case+1] or c.y~=1 or phys(p+1)~=p+1-0x8000 then bad=bad+1 end
 reads=reads+1
end
emu.addMemoryCallback(record,emu.callbackType.exec,0x8DFA,0x8DFA)
emu.addMemoryCallback(record,emu.callbackType.exec,0x8E03,0x8E03)
emu.addMemoryCallback(function()
 if not saved or done then return end
 local p=cases[case+1]
 print(string.format('SHAPE %d %04X %05X %02X %02X %02X %d %d %d',case,p,phys(p+1),r(p+1),r(0x03E2),r(0x03E3),reads,bad,interrupts))
 case=case+1
 if case==#cases then done=true;print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(saved) then done=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0x8E0A,0x8E0A)
emu.addMemoryCallback(function() if saved and not done then interrupts=interrupts+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not done then done=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
