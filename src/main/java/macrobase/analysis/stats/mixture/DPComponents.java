package macrobase.analysis.stats.mixture;

import org.apache.commons.math3.special.Gamma;

public class DPComponents implements MixingComponents {

    // Number of truncated clusters.
    private int T;
    // Concentration parameter for the Dirichlet distribution.
    private double concentrationParameter;

    // Parameters describing stick lengths, i.e. shape parameters of Beta distributions.
    private double shapeParams[][];

    public DPComponents(double concentrationParameter, int T) {
        this.T = T;
        this.concentrationParameter = concentrationParameter;
        shapeParams = new double[T][2];
        for (int i = 0; i < T; i++) {
            shapeParams[i][0] = 1;
            shapeParams[i][1] = concentrationParameter;
        }
    }

    @Override
    public double[] calcExpectationLog() {
        double[] lnMixingContribution = new double[T];
        double cumulativeAlreadyAssigned = 0;
        for (int t = 0; t < T; t++) {
            // Calculate Mixing coefficient contributions to r
            lnMixingContribution[t] = cumulativeAlreadyAssigned + (Gamma.digamma(shapeParams[t][0]) - Gamma.digamma(shapeParams[t][0] + shapeParams[t][1]));
            cumulativeAlreadyAssigned += Gamma.digamma(shapeParams[t][1]) - Gamma.digamma(shapeParams[t][0] + shapeParams[t][1]);
        }
        return lnMixingContribution;
    }

    @Override
    public void update(double[][] r) {
        int N = r.length;
        for (int t = 0; t < shapeParams.length; t++) {
            shapeParams[t][0] = 1;
            shapeParams[t][1] = concentrationParameter;
            for (int n = 0; n < N; n++) {
                shapeParams[t][0] += r[n][t];
                for (int j = t + 1; j < T; j++) {
                    shapeParams[t][1] += r[n][j];
                }
            }
        }
    }

    public double[] getClusterProportions() {
        double[] proportions = new double[T];
        double stickRemaining = 1;
        double expectedBreak;
        for (int i = 0; i < T; i++) {
            expectedBreak = stickRemaining / (1 + shapeParams[i][1] / shapeParams[i][0]);
            stickRemaining -= expectedBreak;
            proportions[i] = expectedBreak;
        }
        return proportions;
    }
}
