-- Conditional FC88 loop entry. Skip waits between individual dispatches;
-- neither this entry nor the injected slot state is ordinary-play evidence.
local saved=nil;local case=0;local step=0;local active=false;local done=false;local frames=0;local nmi=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a) local m=emu.convertAddress(a,emu.memType.nesMemory);return m and m.memType==emu.memType.nesPrgRom and m.address or -1 end
local function dispatch()
 w(0x48,0x10)
 local c=emu.getCpuState();c.pc=0xD54E;emu.setCpuState(c)
end
local function setup()
 step=0;nmi=0
 w(0x10,5);w(0x53,0x88);w(0x54,0x7C);w(0x0365,case)
 w(0x0505,0x55);w(0x0515,0x55);w(0x0535,0);w(0x0755,0);w(0x0665,0);w(0x0685,0);w(0x0545,0xFF)
 for a=0x04E0,0x04EF do w(a,0xFF) end
 w(0x04E5,0)
 for a=0x04B0,0x04D7 do w(a,0) end
 w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 active=true;dispatch()
end
emu.addMemoryCallback(function()
 if saved or done or phys(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function(a,v)
 if active then print(string.format('READ %d %d %04X %05X %02X',case,step+1,a,phys(a),v)) end
end,emu.callbackType.read,0xFC88,0xFC9E)
emu.addMemoryCallback(function()
 if not active then return end
 step=step+1
 print(string.format('STEP %d %d %05X %04X %04X %02X %02X %02X %02X %02X %04X %02X',case,step,phys(0xD568),r(0x53)+256*r(0x54),r(0x05B5)+256*r(0x05C5),r(0x0505),r(0x0515),r(0x0535),r(0x0755),r(0x04D0),r(0x04D4)+256*r(0x04D5),r(0x48)))
 if step<8 then dispatch();return end
 print(string.format('RESULT %d %d',case,nmi));active=false;case=case+1
 if case==2 then done=true;print('DONE 2');emu.stop(0);return end
 if not emu.loadSavestate(saved) then done=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xD568,0xD568)
emu.addMemoryCallback(function() if active then nmi=nmi+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not done then done=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
