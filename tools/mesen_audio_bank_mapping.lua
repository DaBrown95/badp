-- Controlled bank-selection probe: temporarily replace the audio source bank
-- for real CopyToStack calls, then restore the original RAM and mapping.
local frames=0;local next_index=0;local pending=nil;local failures=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
emu.addMemoryCallback(function()
 local pcmap=emu.convertAddress(0x8FF8,emu.memType.nesMemory)
 if not pcmap or pcmap.memType~=emu.memType.nesPrgRom or pcmap.address~=0x0FF8 then return end
 if pending or next_index>=16 then return end
 local state=emu.getState();local x=state['cpu.x'];local lo=r(0x04B4+x);local hi=r(0x04B5+x)
 if hi>=0x80 then return end
 local value=0x0D+next_index*0x10;local index=1+next_index*2;local tablevalue=r(0xFFB7+index)
 pending={oldvalue=r(0x03C2),oldindex=r(0x03C3),value=value,index=index,lo=lo,hi=hi,tablevalue=tablevalue}
 emu.write(0x03C2,value,emu.memType.nesDebug);emu.write(0x03C3,index,emu.memType.nesDebug)
end,emu.callbackType.exec,0x8FF8,0x8FF8)
emu.addMemoryCallback(function()
 if not pending then return end
 local p=r(0xFE)+256*r(0xFF);local m=emu.convertAddress(p,emu.memType.nesMemory)
 local phys=(m and m.memType==emu.memType.nesPrgRom) and m.address or -1
 local expected=0x8000+pending.lo+256*pending.hi
 if p~=0x8000+pending.lo+256*pending.hi or phys~=expected
    or r(0x03C2)~=pending.value or r(0x03C3)~=pending.index then failures=failures+1 end
 print(string.format('BANK %d %02X %02X %02X %04X %05X %05X %02X %02X',next_index,pending.value,pending.index,pending.tablevalue,p,phys,expected,r(0x03C2),r(0x03C3)))
 emu.write(0x03C2,pending.oldvalue,emu.memType.nesDebug);emu.write(0x03C3,pending.oldindex,emu.memType.nesDebug);emu.write(0xFFB7+pending.oldindex,pending.oldvalue,emu.memType.nesMemory)
 pending=nil;next_index=next_index+1
end,emu.callbackType.exec,0xFEC3,0xFEC3)
emu.addEventCallback(function() local start=(frames>=300 and frames<305) or (frames>=900 and frames<905);emu.setInput({up=frames>=180 and frames<185,start=start},0) end,emu.eventType.inputPolled)
emu.addEventCallback(function() frames=frames+1;if next_index==16 or frames==2000 then print(string.format('DONE %d %d %d %d',frames,next_index,failures,pending and 1 or 0));emu.stop(0) end end,emu.eventType.endFrame)
