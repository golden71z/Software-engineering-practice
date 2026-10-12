package com.campus.lostfound.common.exception;

import com.campus.lostfound.common.result.ResultCode;
import lombok.Getter;

/**
 * 业务异常
 * <p>
 * 用于表达可预期的业务规则违反（如"该物品已被认领"），
 * 由全局异常处理器捕获后转换为统一的响应体。
 */
@Getter
public class BusinessException extends RuntimeException {

    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = ResultCode.ERROR.getCode();
    }

    public BusinessException(ResultCode resultCode) {
        super(resultCode.getMessage());
        this.code = resultCode.getCode();
    }

    public BusinessException(ResultCode resultCode, String message) {
        super(message);
        this.code = resultCode.getCode();
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
