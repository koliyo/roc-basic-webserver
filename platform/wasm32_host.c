#include <stddef.h>
#include <stdint.h>

static unsigned char heap[2 * 1024 * 1024];
static size_t heap_used;

void *roc_alloc(size_t size, unsigned int alignment) {
    size_t align = alignment ? (size_t)alignment : 8;
    size_t rem = heap_used % align;
    size_t pad = rem == 0 ? 0 : align - rem;
    if (heap_used + pad + size > sizeof(heap)) {
        return 0;
    }
    heap_used += pad;
    void *ptr = heap + heap_used;
    heap_used += size;
    return ptr;
}

void *roc_realloc(void *ptr, size_t new_size, unsigned int alignment) {
    void *next = roc_alloc(new_size, alignment);
    if (next == 0 || ptr == 0) {
        return next;
    }
    return next;
}

void roc_dealloc(void *ptr, unsigned int alignment) {
    (void)ptr;
    (void)alignment;
}

void roc_panic(void *msg, unsigned int tag_id) {
    (void)msg;
    (void)tag_id;
    __builtin_trap();
}

void *roc_memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = dest;
    const unsigned char *s = src;
    for (size_t i = 0; i < n; i++) {
        d[i] = s[i];
    }
    return dest;
}

void *roc_memset(void *s, int c, size_t n) {
    unsigned char *p = s;
    for (size_t i = 0; i < n; i++) {
        p[i] = (unsigned char)c;
    }
    return s;
}

#define HOSTED_STUB(name)                                              \
    __attribute__((weak)) void name(void) { __builtin_trap(); }

HOSTED_STUB(hosted_cmd_host_exec_exit_code)
HOSTED_STUB(hosted_cmd_host_exec_output)
HOSTED_STUB(hosted_dir_create)
HOSTED_STUB(hosted_dir_create_all)
HOSTED_STUB(hosted_dir_delete_all)
HOSTED_STUB(hosted_dir_delete_empty)
HOSTED_STUB(hosted_dir_list)
HOSTED_STUB(hosted_env_is_windows)
HOSTED_STUB(hosted_env_cwd_unix)
HOSTED_STUB(hosted_env_cwd_windows)
HOSTED_STUB(hosted_env_exe_path_unix)
HOSTED_STUB(hosted_env_exe_path_windows)
HOSTED_STUB(hosted_env_temp_dir)
HOSTED_STUB(hosted_env_var)
HOSTED_STUB(hosted_env_dict)
HOSTED_STUB(hosted_env_current_arch_os)
HOSTED_STUB(hosted_file_delete)
HOSTED_STUB(hosted_file_hard_link)
HOSTED_STUB(hosted_file_is_executable)
HOSTED_STUB(hosted_file_is_readable)
HOSTED_STUB(hosted_file_is_writable)
HOSTED_STUB(hosted_file_read_bytes)
HOSTED_STUB(hosted_file_read_utf8)
HOSTED_STUB(hosted_file_rename)
HOSTED_STUB(hosted_file_size_in_bytes)
HOSTED_STUB(hosted_file_time_accessed)
HOSTED_STUB(hosted_file_time_created)
HOSTED_STUB(hosted_file_time_modified)
HOSTED_STUB(hosted_file_write_bytes)
HOSTED_STUB(hosted_file_write_utf8)
HOSTED_STUB(hosted_path_type)
HOSTED_STUB(hosted_stdout_line)
HOSTED_STUB(hosted_stdout_write)
HOSTED_STUB(hosted_stdout_write_bytes)
HOSTED_STUB(hosted_stderr_line)
HOSTED_STUB(hosted_stderr_write)
HOSTED_STUB(hosted_stderr_write_bytes)
HOSTED_STUB(hosted_unix_time_now)
HOSTED_STUB(hosted_sqlite_open)
HOSTED_STUB(hosted_sqlite_prepare)
HOSTED_STUB(hosted_sqlite_start)
HOSTED_STUB(hosted_sqlite_columns)
HOSTED_STUB(hosted_sqlite_next_row)
HOSTED_STUB(hosted_sqlite_begin)
HOSTED_STUB(hosted_sqlite_txn_prepare)
HOSTED_STUB(hosted_sqlite_txn_finish)
HOSTED_STUB(hosted_tcp_connect)
HOSTED_STUB(hosted_tcp_read_up_to)
HOSTED_STUB(hosted_tcp_read_exactly)
HOSTED_STUB(hosted_tcp_read_until)
HOSTED_STUB(hosted_tcp_write)
HOSTED_STUB(hosted_http_send_request)
HOSTED_STUB(hosted_file_open_reader)
HOSTED_STUB(hosted_file_read_line)
HOSTED_STUB(hosted_sleep_millis)
HOSTED_STUB(hosted_request_body_read)
HOSTED_STUB(hosted_request_body_read_all)
HOSTED_STUB(hosted_readiness_create)
HOSTED_STUB(hosted_readiness_set)
HOSTED_STUB(hosted_request_body_write_file)
