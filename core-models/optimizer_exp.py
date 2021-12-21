#!/usr/bin/env python
# coding: utf-8

import sys
import time
import numpy as np
import pandas as pd
import cvxpy as cp


    
def func(n, ret, risk, GT, lower, upper, CF, BV, tc, w0):
    x = cp.Variable(n, )

    obj = cp.Maximize(ret.T @ x - cp.sum(cp.abs(x - w0)))

    cons = [cp.quad_form(x, Sigma) <= risk, x >= lower, x <= upper, cp.sum(cp.abs(x - w0)) <= tc, cp.sum(x) == (1 + CF/BV)]

    prob = cp.Problem(obj, cons)

    prob.solve(solver='ECOS', verbose=True)
    return x.value


if __name__ == '__main__':
    # 模拟变量
    n_l = 2000
    stock_code = [str(ia) for ia in range(n_l)]
    expect_return = pd.Series(np.random.random(n_l)/10, index=stock_code)
    sys_risk_aversion = 0.5
    special_risk_aversion = 0.5
    cost = 0.03
    period = 'd'
    init_weight = None
    long_short = 'long-only'
    cach_flow_weight = 0
    # 流动性约束
    liquidity = pd.Series(0.05, index=stock_code)
    # 总换手率约束
    tc = 0.5
    # 基准偏离范围
    Shift_b = pd.Series(0.0001, index=stock_code)
    # 传入变量及转化
    np.random.seed(123)
    n = len(expect_return)  # stock num
    print('n=', n)
    lambda_d = special_risk_aversion
    # 风格风险厌恶系数（系统风险厌恶系数）
    lambda_f = sys_risk_aversion

    ret = expect_return.values.reshape((n, 1))  # stock return
    # 风格因子收益率协方差矩阵
    # 先使用假数据，后期接barra数据
    m = 10
    F = np.cov(np.random.random((m, 1000)))
    # 风格因子暴露度
    # # 先使用假数据，后期接barra数据
    X = (np.random.random((m, n)) - 0.5) * 4

    # 特质风险协方差矩阵
    # 使用假数据
    D = np.diag(np.random.uniform(0, 0.09, size=n))
    Sigma = lambda_f * np.dot(np.dot(X.T, F), X) + lambda_d * D
    try:
    #cholesky分解不一定成功，sigma半正定报错
        GT = np.linalg.cholesky(Sigma)  #Cholesky分解
    #使用奇异值分解求解
    except:
        u,s,v = np.linalg.svd(sigma)
        s_square = np.zeros((n, n))
        for i in range(n):
            s_square[i, i] = s[i]
        GT = np.sqrt(lamda) * np.dot(u, np.sqrt(s_square))
    # 基准股票持仓权重
    # 使用假数据
    W_b = np.random.random((n,))
    W_b = W_b / np.sum(W_b)

    # 初始持仓
    w0 = np.ones(n) * (1/n) if init_weight is None else init_weight  # 初始权重
    # 个股流动性约束
    stocks = expect_return.index
    lower = np.max([w0 - liquidity.values, W_b - Shift_b.values], axis=0)
    upper = np.min([w0 + liquidity.values, W_b + Shift_b.values], axis=0)

    CF = 100  # is the cash flow value  理解为初始现金流。PV_0 为初始持仓价值
    BV = 1050  # BV is the base value used for computing asset weights  理解为计算当前权重的基础。
    lambda_tc = 0.01  # Transaction cost multiplier
    risk = 0.05  # 组合风险
    t1 = time.time()
    weights = func(n, ret, risk, GT, lower, upper, CF, BV, tc, w0)
    print('cvxpy consume: {:.4f}, result: {}'.format(time.time() - t1, weights))

