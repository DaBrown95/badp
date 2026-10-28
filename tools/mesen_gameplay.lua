-- The runner supplies SCENARIO as 0 (Noah), 1 (Moses), 2 (David), or 3 (inventory).
-- Inputs and snapshots are deterministic candidates for the pinned v1.5 ROM.
-- Mapper callbacks record the CPU write and the byte currently mapped by Mesen.
local frames=0
local recording=true
local writes=0
local mismatch=0
local unmapped=0
local banks={[0]=false,[1]=false}
local nmis=0
local apu_writes=0
local dma_writes=0
local fetch_probes=0
local record_probes=0
local stage2_record_mode2=0
local inventory_list_zero=0
local inventory_template_zero=0
local inventory_other=0
local script_targets={0x3D21,0x3D22,0x5CFE,0x5D00,0x5D01,0x5D04,0x5D06,0x5D08,0x5D0A}
local record_targets={0x5A40,0x6D71,0x6E65,0x6E7F,0x6ECD,0x6EE5,0x6EFD}
local script_hits={}
local record_hits={}
for _,address in ipairs(script_targets) do script_hits[address]=0 end
for _,address in ipairs(record_targets) do record_hits[address]=0 end
local function hex(s)
 local out={};for i=1,#s do out[i]=string.format('%02x',string.byte(s,i)) end
 return table.concat(out)
end
emu.addMemoryCallback(function(addr,value)
 if not recording then return end
 local m=emu.convertAddress(addr,emu.memType.nesMemory)
 local phys=(m and m.memType==emu.memType.nesPrgRom) and m.address or -1
 local rom=(phys>=0) and emu.read(phys,emu.memType.nesPrgRom) or -1
 writes=writes+1
 if phys<0 then unmapped=unmapped+1 elseif value~=rom then mismatch=mismatch+1 end
 if phys>=0 and phys<0x10000 then banks[math.floor(phys/0x8000)]=true end
 print(string.format('BADP_WRITE %d %04X %02X %d %d',frames,addr,value,phys,rom))
end,emu.callbackType.write,0x8000,0xffff)
local function audio_write(addr,value)
 if not recording then return end
 apu_writes=apu_writes+1
 print(string.format('BADP_APU %d %04X %02X',frames,addr,value))
end
emu.addMemoryCallback(audio_write,emu.callbackType.write,0x4000,0x4013)
emu.addMemoryCallback(audio_write,emu.callbackType.write,0x4015,0x4015)
emu.addMemoryCallback(function(addr,value)
 if not recording then return end
 dma_writes=dma_writes+1
 print(string.format('BADP_DMA %d %04X %02X',frames,addr,value))
end,emu.callbackType.write,0x4014,0x4014)
emu.addEventCallback(function() if recording then nmis=nmis+1 end end,emu.eventType.nmi)
-- Check only the bank-0 interpreter and record-loader entry points. Debug
-- reads have no side effects; candidate identities are encoded pointers.
emu.addMemoryCallback(function()
 if not recording then return end
 local mapped=emu.convertAddress(0xD54E,emu.memType.nesMemory)
 if mapped and mapped.memType==emu.memType.nesPrgRom and mapped.address==0x554E then
  fetch_probes=fetch_probes+1
  local pointer=emu.read(0x53,emu.memType.nesDebug)+256*emu.read(0x54,emu.memType.nesDebug)
  if script_hits[pointer] then script_hits[pointer]=script_hits[pointer]+1 end
 end
end,emu.callbackType.exec,0xD54E,0xD54E)
emu.addMemoryCallback(function()
 if not recording then return end
 local mapped=emu.convertAddress(0xF10C,emu.memType.nesMemory)
 if mapped and mapped.memType==emu.memType.nesPrgRom and mapped.address==0x710C then
  record_probes=record_probes+1
  local pointer=emu.read(0xFE,emu.memType.nesDebug)+256*emu.read(0xFF,emu.memType.nesDebug)
  if record_hits[pointer] then record_hits[pointer]=record_hits[pointer]+1 end
  if pointer==0x36E5 and emu.read(0x03C2,emu.memType.nesDebug)%2==1
     and emu.read(0x57,emu.memType.nesDebug)==2 then
   stage2_record_mode2=stage2_record_mode2+1
  end
 end
end,emu.callbackType.exec,0xF10C,0xF10C)
-- Opcode $54 adds the current slot value to its encoded base before reading
-- two bytes. Observe the two inventory bases without imposing index bounds.
emu.addMemoryCallback(function()
 if not recording then return end
 local mapped=emu.convertAddress(0xDFC3,emu.memType.nesMemory)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=0x5FC3 then return end
 local base=emu.read(0x61,emu.memType.nesDebug)+256*emu.read(0x62,emu.memType.nesDebug)
 if base~=0x505F and base~=0x509D then return end
 local x=emu.read(0x10,emu.memType.nesDebug)
 local index=emu.read(0x70+x,emu.memType.nesDebug)+256*emu.read(0x80+x,emu.memType.nesDebug)
 if index~=0 then inventory_other=inventory_other+1
 elseif base==0x505F then inventory_list_zero=inventory_list_zero+1
 else inventory_template_zero=inventory_template_zero+1 end
end,emu.callbackType.exec,0xDFC3,0xDFC3)
emu.addEventCallback(function()
 local move=frames>=180 and frames<185
 local start=(frames>=300 and frames<305) or (frames>=900 and frames<905)
 local right=frames>=1450 and frames<1750
 local left=false
 local jump=frames>=1500 and frames<1510
 local pickup=false
 if SCENARIO==1 then
  -- Recover Moses at the edge, then cross the position trigger again.
  left=frames>=3320 and frames<3355
  right=((frames>=1450 and frames<1481) or (frames>=1508 and frames<3450))
        and not (frames>=3080 and frames<3100) and not left
  pickup=(frames>=1481 and frames<1491) or (frames>=3290 and frames<3300)
  jump=(frames>=1508 and frames<2000 and ((frames-1508)%220)<28)
       or (frames>=2046 and frames<2074)
       or (frames>=2250 and frames<2700 and ((frames-2250)%190)<28)
       or (frames>=2760 and frames<3000 and ((frames-2760)%190)<16)
       or (frames>=3020 and frames<3036)
       or (frames>=3100 and frames<3128)
       or (frames>=3650 and frames<3660)
  if frames>=3750 then
   left=false
   right=frames<3760 or (frames>=3900 and frames<5700 and not (frames>=4600 and frames<4640)
         and not (frames>=5150 and frames<5170))
   jump=(frames>=3760 and frames<3790) or (frames>=3815 and frames<3843)
        or (frames>=3900 and frames<3928) or (frames>=3960 and frames<3988)
        or (frames>=4065 and frames<4093) or (frames>=4310 and frames<4338)
        or (frames>=4400 and frames<4428) or (frames>=4680 and frames<4708)
        or (frames>=4970 and frames<4998) or (frames>=5280 and frames<5308)
        or (frames>=5385 and frames<5413) or (frames>=5460 and frames<5488)
        or (frames>=5640 and frames<5652)
   pickup=frames>=3855 and frames<3865
  end
 end
 local select=false
 if SCENARIO==3 then
  right=false
  jump=false
  select=(frames>=1500 and frames<1510) or (frames>=2600 and frames<2610)
 end
 emu.setInput({up=move and (SCENARIO==0 or SCENARIO==3),down=move and SCENARIO==2,left=left,right=right,start=start,select=select,a=jump,b=pickup},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frames=frames+1
 if frames==240 or frames==650 or frames==1200 or frames==1400 or frames==1496 or frames==1511 or frames==1550 or frames==1700 or frames==1800 or frames==2100 or frames==2150 or frames==2300 or frames==2400 or frames==2600 or frames==2800 or frames==3000 or frames==3100 or frames==3200 or frames==3250 or frames==3300 or frames==3350 or frames==3400 or frames==3450 or frames==3650 or frames==3700 or frames==3750 or frames==3800 or frames==3825 or frames==3850 or frames==3900 or frames==4050 or frames==4150 or frames==4300 or frames==4400 or frames==4500 or frames==4600 or frames==4650 or frames==4750 or frames==4900 or frames==5000 or frames==5100 or frames==5200 or frames==5250 or frames==5300 or frames==5375 or frames==5450 or frames==5500 or frames==5550 or frames==5575 or frames==5625 or frames==5650 or frames==5700 then
  local state=emu.getState()
  local p=emu.convertAddress(0x8000,emu.memType.nesMemory)
  print(string.format('BADP_FRAME %d %d %d %d %d %d %d %d %s',frames,emu.read(0,emu.memType.nesDebug),emu.read(1,emu.memType.nesDebug),emu.read(0x03ee,emu.memType.nesDebug)+256*emu.read(0x03ef,emu.memType.nesDebug),emu.read(0x03f0,emu.memType.nesDebug)+256*emu.read(0x03f1,emu.memType.nesDebug),p.address,state['cpu.cycleCount'],nmis,hex(emu.takeScreenshot())))
 end
 if frames==1400 or frames==1496 or frames==1511 or frames==1550 or frames==1700 or frames==1800 or frames==2100 or frames==2150 or frames==2300 or frames==2400 or frames==2600 or frames==2800 or frames==3000 or frames==3100 or frames==3200 or frames==3250 or frames==3300 or frames==3350 or frames==3400 or frames==3450 or frames==3650 or frames==3700 or frames==3750 or frames==3800 or frames==3825 or frames==3850 or frames==3900 or frames==4050 or frames==4150 or frames==4300 or frames==4400 or frames==4500 or frames==4600 or frames==4650 or frames==4750 or frames==4900 or frames==5000 or frames==5100 or frames==5200 or frames==5250 or frames==5300 or frames==5375 or frames==5450 or frames==5500 or frames==5550 or frames==5575 or frames==5625 or frames==5650 or frames==5700 then
  print(string.format('BADP_SLOT %d %d %d %d %d %d %d %d %d %d %d %d',frames,
   emu.read(0x04E1,emu.memType.nesDebug),emu.read(0x04E2,emu.memType.nesDebug),
   emu.read(0x06D2,emu.memType.nesDebug),emu.read(0x0582,emu.memType.nesDebug),
   emu.read(0x0592,emu.memType.nesDebug),emu.read(0x0581,emu.memType.nesDebug),
   emu.read(0x0591,emu.memType.nesDebug),emu.read(0x04E3,emu.memType.nesDebug),
   emu.read(0x06D3,emu.memType.nesDebug),emu.read(0x0583,emu.memType.nesDebug),
   emu.read(0x0593,emu.memType.nesDebug)))
 end
 if frames==5700 then
  -- stop() can return before the emulator stops invoking callbacks.
  recording=false
  print(string.format('BADP_SUMMARY %d %d %d %d %d %d %d %d',writes,mismatch,unmapped,banks[0] and 1 or 0,banks[1] and 1 or 0,nmis,apu_writes,dma_writes))
  print(string.format('BADP_PROBE %d %d',fetch_probes,record_probes))
  print(string.format('BADP_STAGE2_RECORD %d',stage2_record_mode2))
  print(string.format('BADP_INVENTORY %d %d %d',inventory_list_zero,inventory_template_zero,inventory_other))
  for _,address in ipairs(script_targets) do print(string.format('BADP_TARGET script %04X %d',address,script_hits[address])) end
  for _,address in ipairs(record_targets) do print(string.format('BADP_TARGET record %04X %d',address,record_hits[address])) end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
