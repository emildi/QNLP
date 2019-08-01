/**
 * @file hamming.hpp
 * @author Myles Doyle (myles.doyle@ichec.ie)
 * @brief Functions to compute the Hamming distance between a test pattern and the states in memory.
 * @version 0.1
 * @date 2019-14-06
 */

#ifndef QNLP_HAMMING
#define QNLP_HAMMING

//#include "Simulator.hpp"
//#include <complex>
#include <cassert>
#include <utility>
#include <memory>
#include <cmath>
#include<vector>
#include<complex>

namespace QNLP{
    template <class SimulatorType>
    class HammingDistanceRotY{
        private:
            //Take the 2x2 matrix type from the template SimulatorType
            using Mat2x2Type = decltype(std::declval<SimulatorType>().getGateX());

            std::size_t len_bin_pattern;

        public:
            HammingDistanceRotY(){};

            HammingDistanceRotY(const std::size_t len_bin_pattern_){
                len_bin_pattern = len_bin_pattern_;
            };

            ~HammingDistanceRotY(){
            };

            /**
             * @brief Adjusts each state's ampitude proportional to the Hamming distanc ebetween the state's training pattern and the test pattern using rotations about y for each mattern qubit. 
             *
             * @param qSim Quantum simulator instance.
             * @param reg_memory A vector containing the indices of the qubits of the memory register. 
             * @param reg_ancilla A vector containing the indices of the qubits of the ancilla register. 
             * @param len_bin_pattern length of binary pattern ie length of memory register.
             */
            void computeHammingDistance(SimulatorType& qSim, 
                    const std::vector<std::size_t>& reg_memory,
                    const std::vector<std::size_t>& reg_ancilla, 
                    std::size_t len_bin_pattern, std::size_t num_bin_patterns){

                double theta = M_PI / (double) num_bin_patterns; 

                std::size_t len_reg_ancilla;
                len_reg_ancilla = reg_ancilla.size();

                // Require length of ancilla register to have n+2 qubits
                assert(reg_memory.size() + 1 < len_reg_ancilla);

                qSim.applyGateH(reg_ancilla[len_reg_ancilla-2]);

                for(std::size_t i = 0; i < len_bin_pattern; i++){
                    qSim.applyGateCX(reg_ancilla[i], reg_memory[i]);
                    qSim.applyGateX(reg_memory[i]);
                }

                for(std::size_t i = 0; i < len_bin_pattern; i++){
                    qSim.applyGateCRotY(reg_ancilla[i],reg_ancilla[len_reg_ancilla-2],theta);
                }

                for(int i = len_bin_pattern-1; i > -1; i--){
                    qSim.applyGateX(reg_memory[i]);
                    qSim.applyGateCX(reg_ancilla[i], reg_memory[i]);
                }
            }


    };

};
#endif


