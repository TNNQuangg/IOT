import java.lang.classfile.ClassFile;
import java.lang.classfile.ClassTransform;
import java.lang.classfile.Opcode;
import java.lang.classfile.instruction.InvokeInstruction;
import java.lang.constant.ClassDesc;
import java.lang.constant.MethodTypeDesc;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.jar.JarFile;

/** Builds a batch-local copy of the engine class with safe wall-clock pacing. */
public class CupCarbonPacing {
    private static final String ENGINE_CLASS = "simulation/WisenSimulation.class";

    public static void main(String[] args) throws Exception {
        byte[] original;
        try (var jar = new JarFile(args[0]);
             var stream = jar.getInputStream(jar.getJarEntry(ENGINE_CLASS))) {
            original = stream.readAllBytes();
        }
        var classFile = ClassFile.of();
        int[] sleepCalls = {0};
        byte[] patched = classFile.transformClass(classFile.parse(original),
                ClassTransform.transformingMethodBodies(
                        method -> method.methodName().equalsString("start_simulation"),
                        (builder, element) -> {
                            if (element instanceof InvokeInstruction call
                                    && call.opcode() == Opcode.INVOKESTATIC
                                    && call.owner().asInternalName().equals("java/lang/Thread")
                                    && call.name().equalsString("sleep")
                                    && call.type().equalsString("(J)V")) {
                                // Some event transitions move the internal clock backward.
                                // Keep the engine's event times and clamp only wall-clock sleep.
                                builder.lconst_0().invokestatic(
                                        ClassDesc.of("java.lang.Math"), "max",
                                        MethodTypeDesc.ofDescriptor("(JJ)J"));
                                sleepCalls[0]++;
                            }
                            builder.with(element);
                        }));
        if (sleepCalls[0] != 2) {
            throw new IllegalStateException("Unexpected CupCarbon pacing implementation: "
                    + sleepCalls[0] + " sleep calls");
        }
        Path output = Path.of(args[1]).resolve(ENGINE_CLASS);
        Files.createDirectories(output.getParent());
        Files.write(output, patched);
        System.out.println("Guarded " + sleepCalls[0] + " pacing calls with Math.max(delay, 0).");
    }
}
