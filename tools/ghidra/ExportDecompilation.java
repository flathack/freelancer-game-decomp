// Export raw decompiler output and function metadata. Output is not buildable or verified source.
//@category Freelancer
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.nio.file.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class ExportDecompilation extends GhidraScript {
    private String clean(String s) { return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' '); }
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Output directory required");
        Path dir = Paths.get(args[0], currentProgram.getName());
        Files.createDirectories(dir);
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(false);
        if (!decompiler.openProgram(currentProgram)) throw new IOException(decompiler.getLastMessage());
        int total = 0, ok = 0, failed = 0;
        try (BufferedWriter code = Files.newBufferedWriter(dir.resolve("raw.c"), StandardCharsets.UTF_8);
             BufferedWriter functions = Files.newBufferedWriter(dir.resolve("functions.tsv"), StandardCharsets.UTF_8);
             BufferedWriter calls = Files.newBufferedWriter(dir.resolve("calls.tsv"), StandardCharsets.UTF_8)) {
            code.write("/* RAW GHIDRA OUTPUT: unverified, incomplete types, not a compilable reconstruction. */\n");
            functions.write("address\tname\tbody_bytes\tthunk\tstatus\terror\n");
            calls.write("caller\tcallee\n");
            FunctionIterator iter = currentProgram.getFunctionManager().getFunctions(true);
            while (iter.hasNext()) {
                monitor.checkCancelled();
                Function f = iter.next();
                total++;
                DecompileResults result = decompiler.decompileFunction(f, 60, monitor);
                boolean success = result.decompileCompleted() && result.getDecompiledFunction() != null;
                String error = result.getErrorMessage();
                functions.write(f.getEntryPoint()+"\t"+clean(f.getName())+"\t"+f.getBody().getNumAddresses()+"\t"+f.isThunk()+"\t"+(success ? "raw_decompiled" : "failed")+"\t"+clean(error == null ? "" : error)+"\n");
                if (success) {
                    ok++;
                    code.write("\n/* Address: "+f.getEntryPoint()+"; name: "+clean(f.getName()).replace("*/","* /")+" */\n");
                    code.write(result.getDecompiledFunction().getC());
                } else failed++;
                for (Function callee : f.getCalledFunctions(monitor))
                    calls.write(f.getEntryPoint()+"\t"+callee.getEntryPoint()+"\n");
                if (total % 500 == 0) { code.flush(); functions.flush(); calls.flush(); println("EXPORT_PROGRESS "+currentProgram.getName()+" "+total+" functions"); }
            }
        } finally { decompiler.dispose(); }
        Files.writeString(dir.resolve("summary.json"), "{\n  \"module\": \""+currentProgram.getName()+"\",\n  \"analyzed_functions\": "+total+",\n  \"raw_decompiled\": "+ok+",\n  \"failed\": "+failed+",\n  \"verified_reconstructions\": 0\n}\n");
        println("EXPORT_DONE "+currentProgram.getName()+" total="+total+" raw="+ok+" failed="+failed);
    }
}
