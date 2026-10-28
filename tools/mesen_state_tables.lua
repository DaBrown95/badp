-- Controlled CPU entry and RAM inputs: this tests table reads, not whether
-- arbitrary state/selector combinations occur during normal gameplay.
local selector_count=256
local saved=nil;local case=0;local active=false;local finished=false;local frames=0;local interrupts=0
local read_trace=0;local bad_reads=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function physical(a)
 local m=emu.convertAddress(a,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom then return -1 end
 return m.address
end
local function setup()
 local state=case%256;local selector=math.floor(case/256)
 w(0x27,state);w(0x61,selector);w(0x10,5);w(0x75,0xA5);w(0x85,0xA5)
 w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 local cpu=emu.getCpuState();cpu.pc=0xE8E3;cpu.x=5;emu.setCpuState(cpu)
 interrupts=0;read_trace=0;bad_reads=0;active=true
end
emu.addMemoryCallback(function()
 if finished or saved then return end
 if physical(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function() if active then interrupts=interrupts+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
local function record_read(tag, base, state_index)
 if not active then return end
 local cpu=emu.getCpuState();local state=case%256
 local expected=state_index and state or ((state*2)%256)
 if cpu.y~=expected or physical(base+cpu.y)~=base+cpu.y-0x8000 then bad_reads=bad_reads+1 end
 read_trace=read_trace*10+tag
end
emu.addMemoryCallback(function() record_read(1,0xA37E,true) end,emu.callbackType.exec,0xE8F2,0xE8F2)
emu.addMemoryCallback(function() record_read(2,0xA395,false) end,emu.callbackType.exec,0xE8FD,0xE8FD)
emu.addMemoryCallback(function() record_read(3,0xA394,false) end,emu.callbackType.exec,0xE902,0xE902)
emu.addMemoryCallback(function() record_read(4,0xA3C1,false) end,emu.callbackType.exec,0xE90D,0xE90D)
emu.addMemoryCallback(function() record_read(5,0xA3C0,false) end,emu.callbackType.exec,0xE912,0xE912)
emu.addMemoryCallback(function()
 if not active then return end
 local cpu=emu.getCpuState();local selector=math.floor(case/256)
 print(string.format('STATE %d %02X %02X %02X %02X %04X %d %d %d',case,case%256,selector,cpu.a,r(0x85),physical(0xE915),interrupts,read_trace,bad_reads))
 active=false;case=case+1
 if case==selector_count*256 then finished=true;print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(saved) then finished=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xE915,0xE915)
emu.addEventCallback(function() frames=frames+1;if frames>=600 and not finished then finished=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
