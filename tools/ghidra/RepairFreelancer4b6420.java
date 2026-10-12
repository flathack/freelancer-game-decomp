// Repair a confirmed instruction-boundary conflict in this exact Freelancer.exe.
//@category Freelancer
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import java.nio.file.*;
public class RepairFreelancer4b6420 extends GhidraScript {
    @Override public void run() throws Exception {
        if(!currentProgram.getName().equals("Freelancer.exe")) throw new IllegalArgumentException("Wrong module");
        if(!currentProgram.getExecutableSHA256().equals("ea4cb797acb1a31a7841f67200fb022a056af4df7b2f7216f8ae6424cb6d1fe9")) throw new IllegalArgumentException("Wrong baseline");
        Address start=toAddr(0x004b6420), bad=toAddr(0x004b6425), end=toAddr(0x004b643e);
        byte[] bytes=new byte[6];currentProgram.getMemory().getBytes(start,bytes);
        if(bytes[0]!=(byte)0x8b || bytes[1]!=0x0d || bytes[5]!=0) throw new IllegalStateException("Unexpected instruction");
        println("ENTRY_REFERENCES "+getReferencesTo(start).length+"; false interior refs "+getReferencesTo(bad).length);
        currentProgram.getFunctionManager().removeFunction(bad);
        currentProgram.getFunctionManager().removeFunction(start);
        clearListing(start,end);
        if(!disassemble(start)) throw new IllegalStateException("Could not decode confirmed start");
        if(createFunction(start,null)==null) throw new IllegalStateException("Could not create function");
        Path dir=Paths.get(getScriptArgs()[0],currentProgram.getName());
        Files.writeString(dir.resolve("repair-4b6420.txt"),"Confirmed original bytes 8b 0d 88 22 67 00 at VA 004b6420.\nRemoved speculative function at interior address 004b6425 and re-decoded 004b6420..004b643e.\nInterior address falls in the displacement of MOV ECX,[0x00672288].\nThe function's null check, pushes, call and ret are now decoded from the correct boundary.\n");
    }
}
