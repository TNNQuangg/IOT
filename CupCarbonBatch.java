import cupcarbon.CupCarbonApp;
import cupcarbon.CupCarbonController;
import device.DeviceList;
import javafx.application.Platform;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.control.TextField;
import javafx.scene.text.Text;
import map.MapLayer;
import map.WorldMap;
import project.Project;
import simulation.SimulationInputs;
import simulation.WisenSimulation;

import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.FutureTask;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

/** Starts the installed CupCarbon engine on a private copy of the project. */
public class CupCarbonBatch {
    private static void openProject(Path project) throws Exception {
        var loader = new FutureTask<Void>(() -> {
            var controller = new CupCarbonController();
            CupCarbonApp.cupCarbonController = controller;
            Map<Class<?>, Supplier<?>> controls = Map.of(
                    Label.class, Label::new, Button.class, Button::new,
                    ProgressBar.class, ProgressBar::new, TextField.class, TextField::new,
                    Text.class, Text::new);
            for (var field : CupCarbonController.class.getDeclaredFields()) {
                var factory = controls.get(field.getType());
                if (factory != null) {
                    field.setAccessible(true);
                    if (field.get(controller) == null) {
                        field.set(controller, factory.get());
                    }
                }
            }
            new WorldMap();
            MapLayer.initLists();
            Project.setProjectName(project.toString(), project.getFileName().toString());
            DeviceList.open();
            return null;
        });
        Platform.startup(loader);
        loader.get(45, TimeUnit.SECONDS);
        // Wait for propagation work queued by DeviceList.open on JavaFX.
        var initialized = new FutureTask<Void>(() -> null);
        Platform.runLater(initialized);
        initialized.get(45, TimeUnit.SECONDS);
        if (DeviceList.sensors.size() != 11) {
            throw new IllegalStateException("Expected 11 CupCarbon nodes, found " + DeviceList.sensors.size());
        }
    }

    public static void main(String[] args) {
        int status = 1;
        try {
            Path project = Path.of(args[0]).toAbsolutePath();
            int duration = Integer.parseInt(args[1]);
            int pace = Integer.parseInt(args[2]);
            openProject(project);
            SimulationInputs.ack = false;
            SimulationInputs.macLayer = false;
            SimulationInputs.visualDelay = pace;
            SimulationInputs.arrowsDelay = 0;
            SimulationInputs.simulationTime = 1_000_000;
            SimulationInputs.showInConsole = false;
            WisenSimulation.showInConsole = false;
            WisenSimulation engine = new WisenSimulation();
            if (!engine.ready()) {
                throw new IllegalStateException("CupCarbon nodes have missing scripts");
            }
            long[] started = {0};
            long[] stopped = {0};
            PrintStream output = System.out;
            var timer = new ScheduledThreadPoolExecutor(1);
            try {
                System.setOut(new PrintStream(output, true, StandardCharsets.UTF_8) {
                    @Override
                    public void println(String line) {
                        super.println(line);
                        if ("Start Simulation ...".equals(line.strip()) && started[0] == 0) {
                            started[0] = System.nanoTime();
                            super.println("[BATCH_START] target_wall_s=" + duration);
                            timer.schedule(() -> {
                                stopped[0] = System.nanoTime();
                                engine.stopSimulation();
                            }, duration, TimeUnit.SECONDS);
                        }
                    }
                });
                engine.start_simulation();
                double elapsed = (System.nanoTime() - started[0]) / 1e9;
                if (started[0] == 0 || elapsed < duration || stopped[0] == 0) {
                    throw new IllegalStateException("CupCarbon ended before completing its active wall-time window");
                }
                output.printf(Locale.ROOT, "[BATCH_END] active_wall_s=%.3f sim_s=%.3f%n",
                        elapsed, WisenSimulation.sTime);
                status = 0;
            } finally {
                timer.shutdownNow();
                System.setOut(output);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.exit(status);
    }
}
