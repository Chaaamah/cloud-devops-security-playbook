# syntax=docker/dockerfile:1
FROM golang:1.24 AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/checkout ./cmd/checkout

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/checkout /checkout
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/checkout"]
